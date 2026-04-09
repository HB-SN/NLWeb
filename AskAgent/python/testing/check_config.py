#!/usr/bin/env python3
"""
Check current configuration to debug test issues
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.config import CONFIG

print("🔍 Checking NLWeb Configuration")
print("="*50)

print("\n📝 Write Endpoint:")
print(f"   {CONFIG.write_endpoint}")

print("\n🗄️ Enabled Retrieval Endpoints:")
for name, config in CONFIG.retrieval_endpoints.items():
    if config.enabled:
        print(f"   {name}:")
        print(f"      - db_type: {config.db_type}")
        print(f"      - api_endpoint: {config.api_endpoint}")
        print(f"      - has_api_key: {'Yes' if config.api_key else 'No'}")

print("\n🔐 Embedding Configuration:")
print(f"   Preferred Provider: {CONFIG.preferred_embedding_provider}")
for name, config in CONFIG.embedding_providers.items():
    print(f"   {name}:")
    print(f"      - model: {config.model}")
    print(f"      - has_api_key: {'Yes' if config.api_key else 'No'}")
    print(f"      - endpoint: {config.endpoint}")

print("\n🗺️ Azure Maps Configuration:")
maps_endpoint = os.getenv("AZURE_MAPS_ENDPOINT")
maps_client_id = os.getenv("AZURE_MAPS_CLIENT_ID")
maps_auth_method = os.getenv("AZURE_MAPS_AUTH_METHOD", "api_key")
print(f"   Endpoint: {maps_endpoint or '❌ Not Set'}")
print(f"   Client ID: {maps_client_id or '❌ Not Set'}")
print(f"   Auth Method: {maps_auth_method}")

if maps_endpoint and maps_client_id:
    import requests
    print("   Testing geocode API...")
    headers = {"x-ms-client-id": maps_client_id}
    if maps_auth_method == "azure_ad":
        try:
            from azure.identity import DefaultAzureCredential
            credential = DefaultAzureCredential()
            token = credential.get_token("https://atlas.microsoft.com/.default")
            headers["Authorization"] = f"Bearer {token.token}"
            print("   ✅ Acquired Azure AD token")
        except Exception as e:
            print(f"   ❌ Failed to acquire Azure AD token: {e}")
            headers = None
    else:
        maps_api_key = os.getenv("AZURE_MAPS_API_KEY")
        if maps_api_key:
            headers["subscription-key"] = maps_api_key
        else:
            print("   ❌ AZURE_MAPS_API_KEY not set")
            headers = None

    if headers:
        try:
            url = f"{maps_endpoint}/geocode?api-version=2025-01-01&query=London,UK"
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code == 200:
                features = resp.json().get("features", [])
                print(f"   ✅ Geocode OK — returned {len(features)} result(s)")
            else:
                print(f"   ❌ Geocode failed: HTTP {resp.status_code} — {resp.text[:200]}")
        except Exception as e:
            print(f"   ❌ Geocode request error: {e}")
else:
    print("   ⚠️ Skipping Maps connectivity test (missing endpoint or client ID)")

print("\n📋 Environment Variables Check:")
env_vars = [
    "AZURE_VECTOR_SEARCH_API_KEY",
    "AZURE_VECTOR_SEARCH_ENDPOINT",
    "NLWEB_WEST_API_KEY",
    "NLWEB_WEST_ENDPOINT",
    "AZURE_OPENAI_API_KEY",
    "AZURE_OPENAI_ENDPOINT"
]

for var in env_vars:
    value = os.getenv(var)
    status = "✅ Set" if value else "❌ Not Set"
    print(f"   {var}: {status}")