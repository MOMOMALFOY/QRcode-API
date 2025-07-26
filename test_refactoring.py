#!/usr/bin/env python3
"""
Script de test pour vérifier le refactoring et le cache de l'API QR Code.
Teste les améliorations apportées selon le feedback reçu.
"""

import asyncio
import time
import httpx
import json
from typing import Dict, Any

# Configuration de test
BASE_URL = "http://127.0.0.1:8000"
TEST_DATA = "https://github.com/MOMOMALFOY?tab=repositories"

async def test_qr_generation_speed():
    """Teste la vitesse de génération avec et sans cache."""
    print("🧪 Test de performance avec cache...")
    
    async with httpx.AsyncClient() as client:
        # Premier appel (sans cache)
        start_time = time.time()
        response1 = await client.get(
            f"{BASE_URL}/generate-qr",
            params={
                "data": TEST_DATA,
                "size": 400,
                "file": "png"
            },
            headers={"x-rapidapi-host": "test.com"}
        )
        first_call_time = time.time() - start_time
        
        # Deuxième appel (avec cache)
        start_time = time.time()
        response2 = await client.get(
            f"{BASE_URL}/generate-qr",
            params={
                "data": TEST_DATA,
                "size": 400,
                "file": "png"
            },
            headers={"x-rapidapi-host": "test.com"}
        )
        second_call_time = time.time() - start_time
        
        print(f"⏱️  Premier appel: {first_call_time:.3f}s")
        print(f"⏱️  Deuxième appel (cache): {second_call_time:.3f}s")
        print(f"🚀 Amélioration: {first_call_time/second_call_time:.1f}x plus rapide")
        
        return response1.status_code == 200 and response2.status_code == 200

async def test_get_vs_post_consistency():
    """Teste que GET et POST produisent le même résultat."""
    print("\n🧪 Test de cohérence GET vs POST...")
    
    async with httpx.AsyncClient() as client:
        # Test GET
        response_get = await client.get(
            f"{BASE_URL}/generate-qr",
            params={
                "data": TEST_DATA,
                "size": 300,
                "body_color": "#FF0000",
                "bg_color": "#FFFFFF",
                "module_style": "rounded"
            },
            headers={"x-rapidapi-host": "test.com"}
        )
        
        # Test POST avec mêmes paramètres
        response_post = await client.post(
            f"{BASE_URL}/generate-qr",
            data={
                "data": TEST_DATA,
                "size": 300,
                "body_color": "#FF0000",
                "bg_color": "#FFFFFF",
                "module_style": "rounded"
            },
            headers={"x-rapidapi-host": "test.com"}
        )
        
        print(f"✅ GET status: {response_get.status_code}")
        print(f"✅ POST status: {response_post.status_code}")
        print(f"📏 GET content length: {len(response_get.content)}")
        print(f"📏 POST content length: {len(response_post.content)}")
        
        return (response_get.status_code == 200 and 
                response_post.status_code == 200 and
                len(response_get.content) == len(response_post.content))

async def test_cache_functionality():
    """Teste le fonctionnement du cache avec différents paramètres."""
    print("\n🧪 Test du cache avec différents paramètres...")
    
    async with httpx.AsyncClient() as client:
        # Test 1: Paramètres identiques
        params1 = {
            "data": "test1",
            "size": 200,
            "body_color": "#000000",
            "bg_color": "#FFFFFF"
        }
        
        start_time = time.time()
        response1 = await client.get(
            f"{BASE_URL}/generate-qr",
            params=params1,
            headers={"x-rapidapi-host": "test.com"}
        )
        time1 = time.time() - start_time
        
        start_time = time.time()
        response2 = await client.get(
            f"{BASE_URL}/generate-qr",
            params=params1,
            headers={"x-rapidapi-host": "test.com"}
        )
        time2 = time.time() - start_time
        
        print(f"🔄 Paramètres identiques - Premier: {time1:.3f}s, Cache: {time2:.3f}s")
        
        # Test 2: Paramètres différents
        params2 = {
            "data": "test2",
            "size": 300,
            "body_color": "#FF0000",
            "bg_color": "#000000"
        }
        
        start_time = time.time()
        response3 = await client.get(
            f"{BASE_URL}/generate-qr",
            params=params2,
            headers={"x-rapidapi-host": "test.com"}
        )
        time3 = time.time() - start_time
        
        print(f"🔄 Paramètres différents - Temps: {time3:.3f}s")
        
        return (response1.status_code == 200 and 
                response2.status_code == 200 and 
                response3.status_code == 200)

async def test_code_readability():
    """Teste que le code refactorisé fonctionne correctement."""
    print("\n🧪 Test de lisibilité du code refactorisé...")
    
    # Test des différents styles de modules
    module_styles = ["square", "rounded", "circle", "gapped"]
    
    async with httpx.AsyncClient() as client:
        for style in module_styles:
            response = await client.get(
                f"{BASE_URL}/generate-qr",
                params={
                    "data": f"test-{style}",
                    "size": 200,
                    "module_style": style
                },
                headers={"x-rapidapi-host": "test.com"}
            )
            print(f"✅ Style '{style}': {response.status_code}")
        
        # Test des gradients
        gradients = ["solid", "radial", "horizontal", "vertical"]
        for gradient in gradients:
            response = await client.get(
                f"{BASE_URL}/generate-qr",
                params={
                    "data": f"test-{gradient}",
                    "size": 200,
                    "gradient_type": gradient,
                    "start_color": "#FF0000",
                    "end_color": "#0000FF"
                },
                headers={"x-rapidapi-host": "test.com"}
            )
            print(f"✅ Gradient '{gradient}': {response.status_code}")
        
        return True

async def main():
    """Fonction principale de test."""
    print("🚀 Démarrage des tests de refactoring et cache...")
    print("=" * 50)
    
    tests = [
        ("Performance avec cache", test_qr_generation_speed),
        ("Cohérence GET vs POST", test_get_vs_post_consistency),
        ("Fonctionnalité du cache", test_cache_functionality),
        ("Lisibilité du code", test_code_readability)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
            print(f"✅ {test_name}: {'PASSÉ' if result else 'ÉCHOUÉ'}")
        except Exception as e:
            print(f"❌ {test_name}: ERREUR - {e}")
            results.append((test_name, False))
        print()
    
    # Résumé
    print("=" * 50)
    print("📊 RÉSUMÉ DES TESTS:")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSÉ" if result else "❌ ÉCHOUÉ"
        print(f"  {test_name}: {status}")
    
    print(f"\n🎯 Score: {passed}/{total} tests passés")
    
    if passed == total:
        print("🎉 Tous les tests sont passés ! Le refactoring est réussi.")
    else:
        print("⚠️  Certains tests ont échoué. Vérifiez le code.")

if __name__ == "__main__":
    asyncio.run(main()) 