#!/usr/bin/env python3
"""Refresh realtime overdose data from open Medical Examiner APIs."""
import urllib.request, urllib.parse, json, os

def fetch_json(url, timeout=120):
    return json.loads(urllib.request.urlopen(url, timeout=timeout).read())

rt = []

# ---- Cook County IL (daily updates) ----
print("Fetching Cook County IL...")
try:
    cook = fetch_json(
        "https://datacatalog.cookcountyil.gov/resource/cjeq-bs86.json?"
        "$limit=5000"
        "&$where=latitude%20IS%20NOT%20NULL"
        "%20AND%20death_date%20%3E%20%272024-01-01%27"
        "%20AND%20(primarycause%20like%20%27%25OVERDOSE%25%27"
        "%20OR%20primarycause%20like%20%27%25OPIOID%25%27"
        "%20OR%20primarycause%20like%20%27%25FENTANYL%25%27"
        "%20OR%20primarycause%20like%20%27%25HEROIN%25%27"
        "%20OR%20primarycause%20like%20%27%25COCAINE%25%27"
        "%20OR%20primarycause_linea%20like%20%27%25OVERDOSE%25%27"
        "%20OR%20primarycause_linea%20like%20%27%25FENTANYL%25%27"
        "%20OR%20primarycause_linea%20like%20%27%25HEROIN%25%27)")
    for r in cook:
        lat, lon = r.get('latitude'), r.get('longitude')
        dd = (r.get('death_date','') or r.get('incident_date',''))[:10]
        cause = (r.get('primarycause','') or 'Drug overdose')[:80]
        city = r.get('incident_city','Chicago')
        if lat and lon and dd:
            rt.append({"la":round(float(lat),4),"lo":round(float(lon),4),
                       "d":dd,"c":cause,"p":f"{city}, IL","s":"Cook County ME"})
    print(f"  -> {len(cook)} records")
except Exception as e:
    print(f"  ERROR: {e}")

# ---- Connecticut OCME ----
print("Fetching Connecticut...")
try:
    ct = fetch_json(
        "https://data.ct.gov/resource/rybz-nyjw.json?" + urllib.parse.urlencode({
            "$limit": 5000,
            "$where": "date > '2024-01-01' AND injurycitygeo IS NOT NULL",
            "$order": "date DESC"
        }))
    for r in ct:
        geo = r.get('injurycitygeo', {})
        lat, lon = geo.get('latitude'), geo.get('longitude')
        dd = (r.get('date',''))[:10]
        cause = (r.get('cod','') or 'Drug overdose')[:80]
        city = r.get('injurycity','CT')
        if lat and lon and dd:
            rt.append({"la":round(float(lat),4),"lo":round(float(lon),4),
                       "d":dd,"c":cause,"p":f"{city}, CT","s":"CT OCME"})
    print(f"  -> {len(ct)} records")
except Exception as e:
    print(f"  ERROR: {e}")

# ---- Santa Clara County CA ----
print("Fetching Santa Clara County CA...")
try:
    sc = fetch_json(
        "https://data.sccgov.org/resource/s3fb-yrjp.json?" + urllib.parse.urlencode({
            "$limit": 50000,
            "$where": "latitude IS NOT NULL AND (cause_of_death like '%overdose%' OR cause_of_death like '%fentanyl%' OR cause_of_death like '%heroin%' OR cause_of_death like '%cocaine%' OR cause_of_death like '%opioid%' OR cause_of_death like '%intoxication%')"
        }))
    for r in sc:
        lat, lon = r.get('latitude'), r.get('longitude')
        dd = (r.get('death_date',''))[:10]
        cause = (r.get('cause_of_death','') or 'Drug overdose')[:80]
        city = r.get('incident_city') or r.get('death_city') or 'Santa Clara County'
        if lat and lon and dd:
            rt.append({"la":round(float(lat),4),"lo":round(float(lon),4),
                       "d":dd,"c":cause,"p":f"{city}, CA","s":"Santa Clara ME"})
    print(f"  -> {len(sc)} records")
except Exception as e:
    print(f"  ERROR: {e}")

# Sort by date descending and write
rt.sort(key=lambda x: x['d'], reverse=True)
outpath = 'realtime_od.json'
with open(outpath, 'w') as f:
    json.dump(rt, f)
print(f"\nTotal: {len(rt)} records -> {outpath}")
print(f"Date range: {rt[-1]['d']} to {rt[0]['d']}")
