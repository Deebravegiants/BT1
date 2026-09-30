# [?] adds test that reproduces double spend afer consensus change (#2571)

## Summary
Severity: Unknown
Chain: Iron Fish
Component: iron-fish/ironfish
Published: 2022-11-14
Source: https://github.com/iron-fish/ironfish/commit/06f7fd4e379109b5a1754b7601a8a281365ac331
Type: security-commit

## Details
adds test that reproduces double spend afer consensus change (#2571)

* adds test that reproduces double spend afer consensus change

1. create a transaction
2. create a fork with a double spend
3. reorg to a chain without the double spend
4. try to create the double spend again, after the consensus change

this test expects the second double spend to fail because of the consensus
change. however, the test fails because the reorg has removed the nullifier from
the original transaction from the chain nullifiers merkle tree.

* adds comments to test, makes it pass

the passing test reflects the current state of the code that allows nullifier
corruption

## Patch
### ironfish/src/blockchain/__fixtures__/blockchain.test.ts.fixture
```diff
@@ -1620,5 +1620,253 @@
         }
       ]
     }
+  ],
+  "Blockchain does not remove nullifiers from double spends during reorg": [
+    {
+      "id": "a50ce736-6e18-41f2-b937-92695951cef8",
+      "name": "accountA",
+      "spendingKey": "fe4bd34776f5946d29e7a1eaf71d2bf4e281dfd4f87c1661e894c32287a260b0",
+      "incomingViewKey": "6e54c00e07364457dcf401f473078ec04e54a7c69e239bbb86431423f4bf0905",
+      "outgoingViewKey": "be4e8a3e8f6c977d2b3cafad627a7f8731b4ad7881c8e8101141c1ab2e7e3939",
+      "publicAddress": "e0a6673ebd91a915fb5496434c04e1013d31f114e22735ce57301cdc5b9922f3b49b1a290b0cffa1b3691b"
+    },
+    {
+      "id": "889ab260-acba-4cc6-b63c-647cdf018b19",
+      "name": "accountB",
+      "spendingKey": "573de70686d4b2cf42f76c2588195775f340ef7ca029586b6c08a12902354b92",
+      "incomingViewKey": "57941414c389efdbae2b3ceef69bc351d628ac77903f5c834c5bc6220878b702",
+      "outgoingViewKey": "13483e8dba1b4b2402a2e222a096a16f7536a140e45421266d920d06ebad303c",
+      "publicAddress": "282451339d9e367a4db0fdb6fb14d489f872f606f15acc58cbf46207453858a9b579811e451960acb9bb4a"
+    },
+    {
+      "header": {
+        "sequence": 2,
+        "previousBlockHash": "69E263E931FA1A2A4B0437A8EFF79FFB7A353B6384A7AEAC9F90AC12AE4811EF",
+        "noteCommitment": {
+          "commitment": {
+            "type": "Buffer",
+            "data": "base64:Rvk/PmBnQyJtpCbdTl23SADWiRGkYi9MUhEzrYJB4kA="
+          },
+          "size": 4
+        },
+        "nullifierCommitment": {
+          "commitment": "E2484D0BF38F29EFFD63EF9D5A61202F198129862B12845182A4CA77AA557A4B",
+          "size": 1
+        },
+        "target": "12167378078913471945996581698193578003257923478462384564023044230",
+        "randomness": "0",
+        "timestamp": 1668385899304,
+        "minersFee": "-2000000000",
+        "work": "0",
+        "hash": "E2490642DAEB014D7AD40AD2105D3206C5418B17FFF59A614CA03138969AE159",
+        "graffiti": "0000000000000000000000000000000000000000000000000000000000000000"
+      },
+      "transactions": [
+        {
+          "type": "Buffer",
+          "data": "base64:AAAAAAAAAAABAAAAAAAAAABsyoj/////AAAAAIHgkXsBGaga/GQdzNyfm6fvZVVW77tFR/Yb1THIk2z1rvnDPs+KAJCGvdw5MA/eZYFf9IZCvEDFh1Rp96G+4Ln9153dLJatQdlhHh9JIkzMZkCMNFXQg/pewXroggGj/wNOzC9xM2Cz9rcSSLuKS4NJnQP4ZGy0r9R6uSWfo9lZUGXiPK5lkATglSB58GLYXLmQdlkt7wcJd3ZNwipKdIWHbRiaNgzAHL+YEcJUTjLJkOGs0rh+E4GoJOP+pIFIwcllEyD08//74LGSMLrHOjVwrUW9Ao4Xd1K43lgibGWK9iaA++EbbYjQsKzDwXexYtv0c0DEhNcZnTuK1SXZFA4tfGMORn9xm2i53TR31BiFXyqHsht54qEKYfI0LTNd5OOZ3u1d4TVfTRErfSQ0WF1eQGUgkPtGivbZvwTdw+PgUV4Fko9nMeL8sOmCEewRvxU3cJGTAybZd//vd2FxMKfOtFo09cfOxdTB0Gy6alJMUB4i6Ydcc6KpA90T0imouSeP5UJlYW5zdGFsayBub3RlIGVuY3J5cHRpb24gbWluZXIga2V5MDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwkrbEJ/44AR6FZcXzhH8Fq6EARlDQrZ2l9UBQp4zLpWH30kuiosc328hcVkB2Hh8pzKmHl5y5u3oSQN2C+wH/BA=="
+        }
+      ]
+    },
+    {
+      "type": "Buffer",
+      "data": "base64:AQAAAAAAAAACAAAAAAAAAAAAAAAAAAAAAAAAAKosFWPzHiWtH2ngtjyfD7Kge82ZQmtdksNctlLgyw4jqRgySHdr3DjBhaaAothTIoGUIXRHPG9Q5kLg/EwuiYKu+V6zcVfUVVLRq5/M6Fmnr3dNuWoc4q+d6dfA0VDoWhkRcNFCahx6SxMpFegDycZpZieSfs7JHvU8mzwD2DmE724nhm8prv+cGHShNNl9R65ytmTpokvPQVd6Oh4TgKAjbb0OTsY50WvRvTgM3xCAuW64bnZBUnpa1wrsWFVANGXvJVOzv/0M06uln0h672JMEASC6jxKk7o9bB0OgL7O/rz/FSB/4sU4uLvyeHR6TDaa9fuzP1XT/qJw8u6NcSVG+T8+YGdDIm2kJt1OXbdIANaJEaRiL0xSETOtgkHiQAQAAADH8fu39Z4WmW7QGAPm67SkaGqrHWjHqswosla536lkGKTMXxrf9OioqES3tWSvmPha2eGxDO9XYzyPCz0K93EC4uW3po2Askr2Wxez0vO/OGQVE65vVui/vUHFFWbtVQWY/p8ELbAe9hc+qKVr5jen5joyevnvNFcLBrMYitYtOMeCXzap+VJFEGx4H4NwL5+L1SnxRM5CRnF/7xnZHMmnOGef7eEX83N98LKsaLlo19jkncyV0lHnkwVtjIvEj5cGLGHaidSN2OQhoQgLj/EkzWDeF0TOA6/m9bXWbYdSXrOnh1Dj96Q024F6dVPdFuiWBPLVxZ1ziBxj9jVGl8R1OyS3j9JHTIIAI/XDYYhlTixaQG/pZ9hUmA4MAA0TNKTztTdcKXQCS25oFBtcWNI0cLvwBykkOaV5ksMptai+8fjmhagx3FkPPekFjdv0DniZCle0d0i90UtaLFgJPJgxWcRHMfaQ1HXKjRdG0gq5K2Kh1deuwGNSHdtSsxCGPa5tsn5s2j8Cor4tId0CnTLg6/PW98Pa/nOo5Xpjtd7D6255TEBXdeKv2jZlArMP9PekRt+awB2a323u1lvcZ18SVEh0R3RD9i9XgZieQXgcnrHwiKAcj9MwaOMEzpEXCzCynn1laVRjsPW1OepgnmBj1O3Yxws14kSe6NE/QKOFfw8A+7QD9FgcVWUwQdgRH+9QCmbcu2E+R22goJZiOtfh+kBrT44VJeoLOyshsclBvuUEiojSIZ+KlfdoNEo+TY6DlWntDmH7oqMLFIbNm3LXDWaF3Rv6MuYS+5HvvOoB0AGGDLas1otBQQvAYI+MwOTuypBXMUpLaUmmDNe26A90hlYkwnHynC/Er7B2mKkzgtjB4RXcFo5hLNwv5xoJN4LW7VNls48dAeGeMM7nIpkkJrLZWzkHMjfMEpwhjyUhrhRKM69qFiykmSDThDEEidMVNEgN1Y4QicTwrTiIh3APkGNqGqUvChInJy+DCGMLMiYXEq7H70HHMDl2UNZZFI6IOvbQXkpFgFbawJtUUpwzQg4kl7x+qxNFdT44c4RmQTUSAX0Bw1maU0N5AubgsBIs5BfXspAFXkacw8ATG5jMO31ZNJgspnNFi+efGgPoXJQFrhdy0yANHHcjqKLC+GrpP+3aERSzFhHU/E6w44DRbsN+AxZWFiCh9h3zssoIaliZeP5arfYKC1SEWgACDmgT+/r4+r5WN6dmd3sQzsc8buNgyuqAsBvD4FuxmJGPn/VHBfCGxaa0MECdb2jgoXj5xcExne54+yUZGmlu7KVOH6ECpZ9guKXCMj9c0UAl7PMFl4XG1K5FtBkGPQvyaJifiOv0rBYGapRcs9PDGTZ3I1I3hF8fUSbngGGVLWV2cHrXe17NkLrEQ78/aGAyotqssvfEcSFbYvf3C7DZLHHW8eyDITEovyCbSxQPxm/9YJYOyddtBQ=="
+    },
+    {
+      "header": {
+        "sequence": 3,
+        "previousBlockHash": "E2490642DAEB014D7AD40AD2105D3206C5418B17FFF59A614CA03138969AE159",
+        "noteCommitment": {
+          "commitment": {
+            "type": "Buffer",
+            "data": "base64:egxmNuZObCIfXJntq8a4orQg4mcJQjC386BaXl91YlI="
+          },
+          "size": 7
+        },
+        "nullifierCommitment": {
+          "commitment": "373B4F54F3BF2382FEC1395B0FF2DB1C2F101B094526FF264C1604E0390297A4",
+          "size": 2
+        },
+        "target": "12131835591833296355903882315508391652467087441833704656133504637",
+        "randomness": "0",
+        "timestamp": 1668385901685,
+        "minersFee": "-2000000000",
+        "work": "0",
+        "hash": "8A56ABED71C97F00B9191F8B40DD4C54A9E19A61A76FE473202B5F54458CF81D",
+        "graffiti": "0000000000000000000000000000000000000000000000000000000000000000"
+      },
+      "transactions": [
+        {
+          "type": "Buffer",
+          "data": "base64:AAAAAAAAAAABAAAAAAAAAABsyoj/////AAAAAIB6Z7D3B0/b+8NvQCLc9ORTdlL/FhWEh/AOhVO6Df48i0El+tObwDeLdISOWJKmcZAzRjzzbxSsHth0HNaNF47z/mMsHo0o12ch7C7kcPCi7RzUlWUzI0TSJXDYBpq6nxCuK7h2UPcpwCM+YIG1YXyBI/uHPz3BXBhT5vt8vLn4m9W2fkm1T9vUkT4E0O3cbJhnlc3AE20U9KWe/4uWK+zpbogkUSVuETWtfAvv/p2gUuCibGwOElos3ELymSlAxoYv6Noj33sthGNewL+Tvubx6sDPJnXSVLfxXca0DJCiFPSNzAzR2PwUuwgpQFN5GqUDFLkdvd1eAfVOrbMQzjczwn0VymI+d0h1AZK8rjU5AvtEQJu9N+S2qoP1Xqx78m/WryL2FiTbjMiyXbG0XGKe+tqjjfpBllqAUUmcCkpOqKuFCE5P6Wr8Xh1Jmqxn6eP6MQWoH6ortP8cuLLpevsYz9blz/q+Il7aEh1eVp9c1trsy95fhkNcgsbPqi4hAlkOvUJlYW5zdGFsayBub3RlIGVuY3J5cHRpb24gbWluZXIga2V5MDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwrZcCR4I7fzhnl8e4G6Kb1Hrj8CN/8jqaR5k7sPh75ExSkXnS4zRf9zZORPBrLxR+3sQgvA2wHcEbLTU/TOBDBA=="
+        },
+        {
+          "type": "Buffer",
+          "data": "base64:AQAAAAAAAAACAAAAAAAAAAAAAAAAAAAAAAAAAKosFWPzHiWtH2ngtjyfD7Kge82ZQmtdksNctlLgyw4jqRgySHdr3DjBhaaAothTIoGUIXRHPG9Q5kLg/EwuiYKu+V6zcVfUVVLRq5/M6Fmnr3dNuWoc4q+d6dfA0VDoWhkRcNFCahx6SxMpFegDycZpZieSfs7JHvU8mzwD2DmE724nhm8prv+cGHShNNl9R65ytmTpokvPQVd6Oh4TgKAjbb0OTsY50WvRvTgM3xCAuW64bnZBUnpa1wrsWFVANGXvJVOzv/0M06uln0h672JMEASC6jxKk7o9bB0OgL7O/rz/FSB/4sU4uLvyeHR6TDaa9fuzP1XT/qJw8u6NcSVG+T8+YGdDIm2kJt1OXbdIANaJEaRiL0xSETOtgkHiQAQAAADH8fu39Z4WmW7QGAPm67SkaGqrHWjHqswosla536lkGKTMXxrf9OioqES3tWSvmPha2eGxDO9XYzyPCz0K93EC4uW3po2Askr2Wxez0vO/OGQVE65vVui/vUHFFWbtVQWY/p8ELbAe9hc+qKVr5jen5joyevnvNFcLBrMYitYtOMeCXzap+VJFEGx4H4NwL5+L1SnxRM5CRnF/7xnZHMmnOGef7eEX83N98LKsaLlo19jkncyV0lHnkwVtjIvEj5cGLGHaidSN2OQhoQgLj/EkzWDeF0TOA6/m9bXWbYdSXrOnh1Dj96Q024F6dVPdFuiWBPLVxZ1ziBxj9jVGl8R1OyS3j9JHTIIAI/XDYYhlTixaQG/pZ9hUmA4MAA0TNKTztTdcKXQCS25oFBtcWNI0cLvwBykkOaV5ksMptai+8fjmhagx3FkPPekFjdv0DniZCle0d0i90UtaLFgJPJgxWcRHMfaQ1HXKjRdG0gq5K2Kh1deuwGNSHdtSsxCGPa5tsn5s2j8Cor4tId0CnTLg6/PW98Pa/nOo5Xpjtd7D6255TEBXdeKv2jZlArMP9PekRt+awB2a323u1lvcZ18SVEh0R3RD9i9XgZieQXgcnrHwiKAcj9MwaOMEzpEXCzCynn1laVRjsPW1OepgnmBj1O3Yxws14kSe6NE/QKOFfw8A+7QD9FgcVWUwQdgRH+9QCmbcu2E+R22goJZiOtfh+kBrT44VJeoLOyshsclBvuUEiojSIZ+KlfdoNEo+TY6DlWntDmH7oqMLFIbNm3LXDWaF3Rv6MuYS+5HvvOoB0AGGDLas1otBQQvAYI+MwOTuypBXMUpLaUmmDNe26A90hlYkwnHynC/Er7B2mKkzgtjB4RXcFo5hLNwv5xoJN4LW7VNls48dAeGeMM7nIpkkJrLZWzkHMjfMEpwhjyUhrhRKM69qFiykmSDThDEEidMVNEgN1Y4QicTwrTiIh3APkGNqGqUvChInJy+DCGMLMiYXEq7H70HHMDl2UNZZFI6IOvbQXkpFgFbawJtUUpwzQg4kl7x+qxNFdT44c4RmQTUSAX0Bw1maU0N5AubgsBIs5BfXspAFXkacw8ATG5jMO31ZNJgspnNFi+efGgPoXJQFrhdy0yANHHcjqKLC+GrpP+3aERSzFhHU/E6w44DRbsN+AxZWFiCh9h3zssoIaliZeP5arfYKC1SEWgACDmgT+/r4+r5WN6dmd3sQzsc8buNgyuqAsBvD4FuxmJGPn/VHBfCGxaa0MECdb2jgoXj5xcExne54+yUZGmlu7KVOH6ECpZ9guKXCMj9c0UAl7PMFl4XG1K5FtBkGPQvyaJifiOv0rBYGapRcs9PDGTZ3I1I3hF8fUSbngGGVLWV2cHrXe17NkLrEQ78/aGAyotqssvfEcSFbYvf3C7DZLHHW8eyDITEovyCbSxQPxm/9YJYOyddtBQ=="
+        }
+      ]
+    },
+    {
+      "header": {
+        "sequence": 4,
+        "previousBlockHash": "8A56ABED71C97F00B9191F8B40DD4C54A9E19A61A76FE473202B5F54458CF81D",
+        "noteCommitment": {
+          "commitment": {
+            "type": "Buffer",
+            "data": "base64:eB/Ffqgkkpmz/xdIn4Ev8r2n2eKEdL5JLEet7ROpMhs="
+          },
+          "size": 10
+        },
+        "nullifierCommitment": {
+          "commitment": "DEA816996E382086E4F8A933E82D9AD844162191D07AEAEB13C052437641A842",
+          "size": 3
+        },
+        "target": "12096396928958695709100635723060514718229275323289987966729581326",
+        "randomness": "0",
+        "timestamp": 1668385901985,
+        "minersFee": "-2000000000",
+        "work": "0",
+        "hash": "F92EE0B7A629ADFF6FD2D10A171136FB5CF355EC4A2D30174B3E546C73F95ADF",
+        "graffiti": "0000000000000000000000000000000000000000000000000000000000000000"
+      },
+      "transactions": [
+        {
+          "type": "Buffer",
+          "data": "base64:AAAAAAAAAAABAAAAAAAAAABsyoj/////AAAAAJn6w5eQLFM8wwLbkrsObaw0AgswlFiDPdsIpHrrAS4b9BW2kg4ouHaUAO9viJM2a7Ot1FG+iGFXZoEm2wfQxY12sQstFETlhHlOUE5EQLgkjFcO3LUaitE910HHhK+DfxM1zd0RVZIkLKF+NxBLSL4dF8VB33mGdSKCCVXTXGUBAVYJXNmmEbXt1KqKUCVmzKf5vcclW9hjtz7uw0gWxu0E3kmgdUXHakk8cFNeRdlIz98VL55ScESp9S2LGS+Nsy5jn5zcmSRZ92iO/bFhRMrQozgYbDne3u3zFl36h4ucTvQ++8yhZMknnhe3kuNVFvBoz8kGUl+d5MnV+Oi/ky1wUwNpgxyTrBGOO1Mg6ShrjatmU6k2L7eyN82R6fnquGj2kP5dMoRbasBF+PDVO70zjA2aenFqJ29cAv7snq27vfrVIuiLUBx6drKffTsdxJM0bH2gpHw4/J/gMCG3Sd3SvI8D/yPVME2ifWSD8t8lsuWlFy+gYOlvCAcF2oIfjbdt0UJlYW5zdGFsayBub3RlIGVuY3J5cHRpb24gbWluZXIga2V5MDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwew/5BLJ3OSZcnKmZ3cGB1dKOBrxgawUbJ0ppCkJvPKEuIxiE4VB1dBwQiB4dnBvRS3LXcAwizYDrHum6eHucAQ=="
+        },
+        {
+          "type": "Buffer",
+          "data": "base64:AQAAAAAAAAACAAAAAAAAAAAAAAAAAAAAAAAAAKosFWPzHiWtH2ngtjyfD7Kge82ZQmtdksNctlLgyw4jqRgySHdr3DjBhaaAothTIoGUIXRHPG9Q5kLg/EwuiYKu+V6zcVfUVVLRq5/M6Fmnr3dNuWoc4q+d6dfA0VDoWhkRcNFCahx6SxMpFegDycZpZieSfs7JHvU8mzwD2DmE724nhm8prv+cGHShNNl9R65ytmTpokvPQVd6Oh4TgKAjbb0OTsY50WvRvTgM3xCAuW64bnZBUnpa1wrsWFVANGXvJVOzv/0M06uln0h672JMEASC6jxKk7o9bB0OgL7O/rz/FSB/4sU4uLvyeHR6TDaa9fuzP1XT/qJw8u6NcSVG+T8+YGdDIm2kJt1OXbdIANaJEaRiL0xSETOtgkHiQAQAAADH8fu39Z4WmW7QGAPm67SkaGqrHWjHqswosla536lkGKTMXxrf9OioqES3tWSvmPha2eGxDO9XYzyPCz0K93EC4uW3po2Askr2Wxez0vO/OGQVE65vVui/vUHFFWbtVQWY/p8ELbAe9hc+qKVr5jen5joyevnvNFcLBrMYitYtOMeCXzap+VJFEGx4H4NwL5+L1SnxRM5CRnF/7xnZHMmnOGef7eEX83N98LKsaLlo19jkncyV0lHnkwVtjIvEj5cGLGHaidSN2OQhoQgLj/EkzWDeF0TOA6/m9bXWbYdSXrOnh1Dj96Q024F6dVPdFuiWBPLVxZ1ziBxj9jVGl8R1OyS3j9JHTIIAI/XDYYhlTixaQG/pZ9hUmA4MAA0TNKTztTdcKXQCS25oFBtcWNI0cLvwBykkOaV5ksMptai+8fjmhagx3FkPPekFjdv0DniZCle0d0i90UtaLFgJPJgxWcRHMfaQ1HXKjRdG0gq5K2Kh1deuwGNSHdtSsxCGPa5tsn5s2j8Cor4tId0CnTLg6/PW98Pa/nOo5Xpjtd7D6255TEBXdeKv2jZlArMP9PekRt+awB2a323u1lvcZ18SVEh0R3RD9i9XgZieQXgcnrHwiKAcj9MwaOMEzpEXCzCynn1laVRjsPW1OepgnmBj1O3Yxws14kSe6NE/QKOFfw8A+7QD9FgcVWUwQdgRH+9QCmbcu2E+R22goJZiOtfh+kBrT44VJeoLOyshsclBvuUEiojSIZ+KlfdoNEo+TY6DlWntDmH7oqMLFIbNm3LXDWaF3Rv6MuYS+5HvvOoB0AGGDLas1otBQQvAYI+MwOTuypBXMUpLaUmmDNe26A90hlYkwnHynC/Er7B2mKkzgtjB4RXcFo5hLNwv5xoJN4LW7VNls48dAeGeMM7nIpkkJrLZWzkHMjfMEpwhjyUhrhRKM69qFiykmSDThDEEidMVNEgN1Y4QicTwrTiIh3APkGNqGqUvChInJy+DCGMLMiYXEq7H70HHMDl2UNZZFI6IOvbQXkpFgFbawJtUUpwzQg4kl7x+qxNFdT44c4RmQTUSAX0Bw1maU0N5AubgsBIs5BfXspAFXkacw8ATG5jMO31ZNJgspnNFi+efGgPoXJQFrhdy0yANHHcjqKLC+GrpP+3aERSzFhHU/E6w44DRbsN+AxZWFiCh9h3zssoIaliZeP5arfYKC1SEWgACDmgT+/r4+r5WN6dmd3sQzsc8buNgyuqAsBvD4FuxmJGPn/VHBfCGxaa0MECdb2jgoXj5xcExne54+yUZGmlu7KVOH6ECpZ9guKXCMj9c0UAl7PMFl4XG1K5FtBkGPQvyaJifiOv0rBYGapRcs9PDGTZ3I1I3hF8fUSbngGGVLWV2cHrXe17NkLrEQ78/aGAyotqssvfEcSFbYvf3C7DZLHHW8eyDITEovyCbSxQPxm/9YJYOyddtBQ=="
+        }
+      ]
+    },
+    {
+      "header": {
+        "sequence": 4,
+        "previousBlockHash": "8A56ABED71C97F00B9191F8B40DD4C54A9E19A61A76FE473202B5F54458CF81D",
+        "noteCommitment": {
+          "commitment": {
+            "type": "Buffer",
+            "data": "base64:HZLElkM9NP87w+eaKpEvnommhSsq1fSroAYzUigEHAw="
+          },
+          "size": 8
+        },
+        "nullifierCommitment": {
+          "commitment": "373B4F54F3BF2382FEC1395B0FF2DB1C2F101B094526FF264C1604E0390297A4",
+          "size": 2
+        },
+        "target": "12096396928958695709100635723060514718229275323289987966729581326",
+        "randomness": "0",
+        "timestamp": 1668385902248,
+        "minersFee": "-2000000000",
+        "work": "0",
+        "hash": "BC35507ECA740888C7F85E70196FC741665DD74B9A7F621F8D1F51A74363D11A",
+        "graffiti": "0000000000000000000000000000000000000000000000000000000000000000"
+      },
+      "transactions": [
+        {
+          "type": "Buffer",
+          "data": "base64:AAAAAAAAAAABAAAAAAAAAABsyoj/////AAAAAKj6nPXl4MISmK0HhJHU2RBGmdIyQhbQrAdeU5MH8jcHY5wTfejQNS5g9hiU+gesOo4qHWP+mlpuQsWt+wGEQ1goeGoXf8LyxGPUnLRFEinC3+Ojkh875HVT+2E8goJq5RPHW7++Nw6HpiC/mszkvMVVwD4F8pNw6l+XDCibJiAU8GJB4G1IWPuux2OCsmWSlaBxj+SkhSHFJpHf41rQqFy/yFF/oa1Yt/LM1f5nWZn50AdY3OykLKS1Fw6JNBYZnRI7C3BFXN1IAcbEiTcxvi2MF3mXe2TYGhFf9tBcJ3kiOCuaiHo9UiNxcGovwsb9Yijr+klPoANqvfE+QIwqXjMJhw2PTPXAWtrkvt9ZciBfYBZ9UYdNdILv5bYBxhJy5lcTvmgIPAkQODIAcVUwY4JtALygZaPKM4w44GBOlwluVniCUYwtZawBEy8xnboXKl75dv+D4kdHvsTIYQ9cJ/TH/sY2BvzfMEv/zWAep3zcIMCR8jSEbDI92dBHM40coUanGUJlYW5zdGFsayBub3RlIGVuY3J5cHRpb24gbWluZXIga2V5MDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwo6hzm1jv+e4z7aHVPbZsVynEpNV5uhgioRDKhL5r7V9uvhwwZwXYl0qnHx4iK4AwnaEn29qcKv0yK+wPDbz5Bg=="
+        }
+      ]
+    },
+    {
+      "header": {
+        "sequence": 5,
+        "previousBlockHash": "BC35507ECA740888C7F85E70196FC741665DD74B9A7F621F8D1F51A74363D11A",
+        "noteCommitment": {
+          "commitment": {
+            "type": "Buffer",
+            "data": "base64:qaB17NvImIJ4rT1sLh5V6Zvws2JD4uR9+bdMFK0U4k0="
+          },
+          "size": 9
+        },
+        "nullifierCommitment": {
+          "commitment": "373B4F54F3BF2382FEC1395B0FF2DB1C2F101B094526FF264C1604E0390297A4",
+          "size": 2
+        },
+        "target": "12061061787010396005823540495362954933337395011119300165635986189",
+        "randomness": "0",
+        "timestamp": 1668385902491,
+        "minersFee": "-2000000000",
+        "work": "0",
+        "hash": "9EAC048CE480C7AAB7666A6A004FFC5100505958FB428531EDA26CD8F121A231",
+        "graffiti": "0000000000000000000000000000000000000000000000000000000000000000"
+      },
+      "transactions": [
+        {
+          "type": "Buffer",
+          "data": "base64:AAAAAAAAAAABAAAAAAAAAABsyoj/////AAAAAKl3IwWoJG/xKXeY3KYXx4FzHxprx6CbCme0+TrEmskMckuPZv9kyiDh6NgdUEjVT6BG7P4aCiZ3sUvTsF9D8MAUOe3RVPKlU3Z43lGR1kfUsVbl0qfKYFKFyte+3eKVlxX5VNtFePSwA13vVL0DFTYtGH0uTxVAkWQTgiZ00JJLDxbejy2MS+u1f2XolkAZUJH7T1SEG00BI2/BzCtcJZBAQcGRLET7KuW8q0ndt6t0rSmCCOxOEW/A/lNjAVCDrZkXobqRfmQDJ1ZsaDXfHdjIyEXRASvmk4C8qUMkTWed8/rQOs6wGcNuhOR8vaedxM7qbfEz51HWEga/I2C3yAplCitwInGr3OMCy2Ie7188qLtgKVKNmTsqpr9XpkMlRcW0SS8Kb4uggnj1Ig5e7ZkxVahZs/c2E98AAdAwAjuI0C4eHl7+WdpPtnesVNUHk9BoRiY33ZUewQTrlh2rD7W0m0F+9rcSD3rxTECk0Hb9SqnT9wjEOSmimyN6swufUHjxO0JlYW5zdGFsayBub3RlIGVuY3J5cHRpb24gbWluZXIga2V5MDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwJJwacYIUFygqIcqzk6+z5UfTvzw1eHoNLvhmnopD651SCw2QMQfp5dp0Bn3O7x/e7n6AFVszrbKOm7b3h3MVDg=="
+        }
+      ]
+    },
+    {
+      "header": {
+        "sequence": 6,
+        "previousBlockHash": "9EAC048CE480C7AAB7666A6A004FFC5100505958FB428531EDA26CD8F121A231",
+        "noteCommitment": {
+          "commitment": {
+            "type": "Buffer",
+            "data": "base64:W2UiZLW30jhChDpKu8+LzlUZx0mgANOvWtEXYZoe1jc="
+          },
+          "size": 12
+        },
+        "nullifierCommitment": {
+          "commitment": "DEA816996E382086E4F8A933E82D9AD844162191D07AEAEB13C052437641A842",
+          "size": 3
+        },
+        "target": "12025829863586302258274667766838505692576214880101876262606819815",
+        "randomness": "0",
+        "timestamp": 1668385902782,
+        "minersFee": "-2000000000",
+        "work": "0",
+        "hash": "12389973F79CC06C499D24C38FE24F22CEF9BDCD0FADCB76E37DBE73B0979C17",
+        "graffiti": "0000000000000000000000000000000000000000000000000000000000000000"
+      },
+      "transactions": [
+        {
+          "type": "Buffer",
+          "data": "base64:AAAAAAAAAAABAAAAAAAAAABsyoj/////AAAAAIo/FUuxg1Dx8hAVmuLPX1H01quDij9nI7HSgqrtPy6NbGOxy5AKza+KDcgtul5t/qZGAUJvY74TTxQh5DgxeWvy9SpciiU5ytWb9bbgpJ202OUzP2Gwm9MZnokzyUFyphgC2Ub8wt+TaV658+Oa/sia+kuZQw++uw0wO1Q6baTcvruJ+VocN4QHIQXJUxReuqmhNuHFwlEosGFowBwl1yKoy74+yHix8spiVlLR4vGgc9pEpbu/ghExpC8mD0YiaILfkJkBfWi3EpmurWuYD8afTbkgroom2AF6yyTmFWjU8/R5u2AGuX+mgvWpIU65a5JVM/anz/Nm0h5HVSzPhgvfFAvOUYPxe7LYhBVKJW3IEnMn2DRw3sWtMwtUUNfDuUq/vDIhwBeRk32cZN4f6TbUvDXSD3Zz0ohwL9IemCjvbyGJQNyT/GCRZmO0J+6FkTDx3U3oFZfKgX4hLohchr3udis64m23qMFmwYsyTtf4Sg7MYydijf8sfakNNqGf43WvLkJlYW5zdGFsayBub3RlIGVuY3J5cHRpb24gbWluZXIga2V5MDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAw8BBN1wejtjKdFpEA2wiwMn2wKS5SSen+lQoJ9TE9ScK/ZnryvjGUw1jOw778sxYz+7hMfUwCAHQCoeTjEuvxCA=="
+        },
+        {
+          "type": "Buffer",
+          "data": "base64:AQAAAAAAAAACAAAAAAAAAAAAAAAAAAAAAAAAAKosFWPzHiWtH2ngtjyfD7Kge82ZQmtdksNctlLgyw4jqRgySHdr3DjBhaaAothTIoGUIXRHPG9Q5kLg/EwuiYKu+V6zcVfUVVLRq5/M6Fmnr3dNuWoc4q+d6dfA0VDoWhkRcNFCahx6SxMpFegDycZpZieSfs7JHvU8mzwD2DmE724nhm8prv+cGHShNNl9R65ytmTpokvPQVd6Oh4TgKAjbb0OTsY50WvRvTgM3xCAuW64bnZBUnpa1wrsWFVANGXvJVOzv/0M06uln0h672JMEASC6jxKk7o9bB0OgL7O/rz/FSB/4sU4uLvyeHR6TDaa9fuzP1XT/qJw8u6NcSVG+T8+YGdDIm2kJt1OXbdIANaJEaRiL0xSETOtgkHiQAQAAADH8fu39Z4WmW7QGAPm67SkaGqrHWjHqswosla536lkGKTMXxrf9OioqES3tWSvmPha2eGxDO9XYzyPCz0K93EC4uW3po2Askr2Wxez0vO/OGQVE65vVui/vUHFFWbtVQWY/p8ELbAe9hc+qKVr5jen5joyevnvNFcLBrMYitYtOMeCXzap+VJFEGx4H4NwL5+L1SnxRM5CRnF/7xnZHMmnOGef7eEX83N98LKsaLlo19jkncyV0lHnkwVtjIvEj5cGLGHaidSN2OQhoQgLj/EkzWDeF0TOA6/m9bXWbYdSXrOnh1Dj96Q024F6dVPdFuiWBPLVxZ1ziBxj9jVGl8R1OyS3j9JHTIIAI/XDYYhlTixaQG/pZ9hUmA4MAA0TNKTztTdcKXQCS25oFBtcWNI0cLvwBykkOaV5ksMptai+8fjmhagx3FkPPekFjdv0DniZCle0d0i90UtaLFgJPJgxWcRHMfaQ1HXKjRdG0gq5K2Kh1deuwGNSHdtSsxCGPa5tsn5s2j8Cor4tId0CnTLg6/PW98Pa/nOo5Xpjtd7D6255TEBXdeKv2jZlArMP9PekRt+awB2a323u1lvcZ18SVEh0R3RD9i9XgZieQXgcnrHwiKAcj9MwaOMEzpEXCzCynn1laVRjsPW1OepgnmBj1O3Yxws14kSe6NE/QKOFfw8A+7QD9FgcVWUwQdgRH+9QCmbcu2E+R22goJZiOtfh+kBrT44VJeoLOyshsclBvuUEiojSIZ+KlfdoNEo+TY6DlWntDmH7oqMLFIbNm3LXDWaF3Rv6MuYS+5HvvOoB0AGGDLas1otBQQvAYI+MwOTuypBXMUpLaUmmDNe26A90hlYkwnHynC/Er7B2mKkzgtjB4RXcFo5hLNwv5xoJN4LW7VNls48dAeGeMM7nIpkkJrLZWzkHMjfMEpwhjyUhrhRKM69qFiykmSDThDEEidMVNEgN1Y4QicTwrTiIh3APkGNqGqUvChInJy+DCGMLMiYXEq7H70HHMDl2UNZZFI6IOvbQXkpFgFbawJtUUpwzQg4kl7x+qxNFdT44c4RmQTUSAX0Bw1maU0N5AubgsBIs5BfXspAFXkacw8ATG5jMO31ZNJgspnNFi+efGgPoXJQFrhdy0yANHHcjqKLC+GrpP+3aERSzFhHU/E6w44DRbsN+AxZWFiCh9h3zssoIaliZeP5arfYKC1SEWgACDmgT+/r4+r5WN6dmd3sQzsc8buNgyuqAsBvD4FuxmJGPn/VHBfCGxaa0MECdb2jgoXj5xcExne54+yUZGmlu7KVOH6ECpZ9guKXCMj9c0UAl7PMFl4XG1K5FtBkGPQvyaJifiOv0rBYGapRcs9PDGTZ3I1I3hF8fUSbngGGVLWV2cHrXe17NkLrEQ78/aGAyotqssvfEcSFbYvf3C7DZLHHW8eyDITEovyCbSxQPxm/9YJYOyddtBQ=="
+        }
+      ]
+    },
+    {
+      "header": {
+        "sequence": 6,
+        "previousBlockHash": "8EAEF39E0080799A0E8AEB2F0D8FB9E68C35FD32D92D0E3B498F5F1707969A78",
+        "noteCommitment": {
+          "commitment": {
+            "type": "Buffer",
+            "data": "base64:liZPeD9rF6Mv+Okpyz9JKqwAk8E3MV0xETSh0edD5RE="
+          },
+          "size": 12
+        },
+        "nullifierCommitment": {
+          "commitment": "A342E354D7B635F7EC85D159D2D8657433806FC6C2B62F5F637DF1FCC9431CCA",
+          "size": 3
+        },
+        "target": "12025829863586302258274667766838505692576214880101876262606819815",
+        "randomness": "0",
+        "timestamp": 1668385823308,
+        "minersFee": "-2000000000",
+        "work": "0",
+        "hash": "345EDC56F00BBE8CB5214697211D1C50055B6314388EF175C78EEEE0A9BD06C7",
+        "graffiti": "0000000000000000000000000000000000000000000000000000000000000000"
+      },
+      "transactions": [
+        {
+          "type": "Buffer",
+          "data": "base64:AAAAAAAAAAABAAAAAAAAAABsyoj/////AAAAAIvfbNr3i8HQwBJhr+Ou04bukvfeqLXvMinvnqZhB1lmFT0Rn5AY12LOY9RJcsAxqK+p/z5BXpZjg02bHJY870tnWdenEn2Po061O9c8feD/n1hF1KqK/V5C4rr4spkpAxmPbEXKSZorbodRumxxoXTAfh4sKsBmsMQJKY7ZYCJ6hb4M/4Ueo487wz3zAaEmyK4PnPXvEsOEdGvmfXgwU8YjCkhvLx8oebb4zQxcIhxb73iXBvycwXW3KwqRQ/ThPEG092hq1gdzZOBKlXdm91nsM9HPnnGTMCHwoC2quRwHErg3BYBp7k/N7nzo572go84kAUuZw46OI2uFAnAih1kerwaCD7RYjSeXRwo3x4beGgeCnVxwfjZgyUMITcQRlws5Ngpo+jdopm85wHgvyb2ptn19ONr6eoI9GfKGZFfrWQtiYoIxdaGKYETBWQk/U0jHnBN5ToyR6gTn7lE15AZkxgeqdItkCGihKMURFZW5L7i1E8ukOeqHAvYWD0DIoZDW0EJlYW5zdGFsayBub3RlIGVuY3J5cHRpb24gbWluZXIga2V5MDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAw+lfbZPi7ZYd5m6jJs0cB+g0NnXRSE4joaEPRChEBP8JATRT7oy0/S0YnAE3ePUp+kHGKJ/hDSkz5/OTguXIeBA=="
+        },
+        {
+          "type": "Buffer",
+          "data": "base64:AQAAAAAAAAACAAAAAAAAAAAAAAAAAAAAAAAAAKnatvisN14XPo8eC+7TKqPsYYPuZv+cLW6qI/co6OM+YPtWBkVSINlSj41yyelAfJLlZwJwWH2ww8b6WKNPXldmX4A91zMbzihRBkCKtnPi4Fjk3e13NjByF9MlUk9RwxcDxfhi7CsPwCchF0Sk+aqcWiySvt3UUvMol27x9yiQAMa7QoBIC5dq/fPEZ0TX+YlN3sNOiRnIjAkBvc196U1UzCHBGCRwWKR6+su7585a3X6FpDdPr+QBcGgLL6Y1Tjsa8b3nqP6XkP2DkE0nCjiRNF+DA8BJojxr/+5K2ODGCuj0VZ6KAeGTkBeNYJqKyUbJdwmwXY9zYn0IaU0KGVJc6orpEdoVHyIWP2YV42JdPOopzrvEzkzFwgJAcFw3DQQAAAC1Dyjfwvbp2X3pnjzqezVWYDevOQE539E+hT9ufJV733+S3LYt+Y2a5WLH0Q1CXGNIj67id1qniXLfOUEoxqBy7xVZ4NIoe8ikYUt3iJME73PHqRuc54uagVD/vOrIAgCVnREIw+8xUGJtLLUcClIt2sHT40qR8KZBoj7B5USuqz7z/r3HudYDscG0K5Q3FIiuSgc0SZyt+TLqZcFK1qO5kIAIzTjkZTO8Ry/HnICHGSW9POxk6654vqR7smmFEFkStl+MTpqU8yz1hom3PKdAprNq2DhoaCSAWzX7EYyu6IX1rDnjuLNdQ89U+6+b29qYUzuDtOSAFtzacFy1/Hhe41qwMG676OAk8VSAUSjjeBLETCbcBpstc81GwxFuNukNWGqmggcr2pIhxepQ3b0aAHZ2wfw4FPIWDQng3tKpVGuLCTZHT/RQY8cioGCOoER67MY1xy9jxTxkc2x8ZeM/SktBfTy8Hc5IW74pYIDTi4N8FdoCXLxR3P2lJTI2YgO9jfN0ie8cvCEleewND5RAeqQPGUjt4yTziyEe0+/dBz9ClfAEYfGjCdxm7z2wpLHRCLIY+biln7K8Lmv+UsLm5nxKDQwPV4mX4hge9JJVclfU8SETiCmKHZZGDYm2l+AvDwVzalz4svVCRSHnV9Yq7f7masSoqOguawJ+4eMWNzyYYm07QE989vElZO8Smx7QTky7YozmQtp/nfw11dgT4OxIiXytEcpbN/nhx9c/VJmmubBKvJfroHsui5AgYoEnUJDu1DyHwYg2N5Tzyr4rKQGsWU+sDJ1BHT4AfrZvhfYlZITJBv2oKSeN7A8LXr7Xw0ZrWiklPcs4N00d6RCJa/DMwKvrk+UovudEabXfFiF6VQc/RRsU1JspzmV2zYxS91IOWusyYIUJQxi+03CouGzEVhlFzvtXkdiPtTv2uE14IJHou2K64YuPHSzhaq9xGi52yWztGz+eV5s6au+DvP/hIQUi8wSWLL543jY1nfQWDGpbLjsJIHK0VclEdCNn7NgpdtFt547a7gqElBnrtJqkEdObEV4KFLEtTuWTYxe3NISCODJDiEg5on5JJsHdGw3wMAWkLDgx0BbieSHXMlr8Zq1uh2fhK+X8KmZ9VTGOERfJV+/nxRqzpco592PFEGRJ1G9k5IW+2qjM0klcdGUYPx6DDXVcN4SNA3LR5h4LJ9aIIsEENTlEHFnrTDnuwjr1uUvGCiZJcGMI6MHuo5NS0ivrGTAZ2pT48cAEKju/plHMulYGvoe0EFbgeUBMPIPFXTWFXopwAaC/wDWD/Mq+G7uUSimO73jPVFe+oDTpZKyNHKQT3gpHOIJECZwnw2k5ZTQ57utz6AEN9q+yy1ozKflsi/uN4Vy8aUOmcN5UvrMFOhtSBSOMdHlgJS5D3Y7AqNOGdKORugkTMwRozpf5sPsSPXXlCInq1/E5FYQi67mIDA=="
+        }
+      ]
+    }
   ]
 }
\ No newline at end of file
```

### ironfish/src/blockchain/blockchain.test.ts
```diff
@@ -901,4 +901,105 @@ describe('Blockchain', () => {
       })
     }
   })
+
+  it('does not remove nullifiers from double spends during reorg', async () => {
+    // chain diagram for test duration, double spend transaction represented as '*'
+    //
+    // nodeA chain
+    // G -> B2 -> B3* -> A4*
+    //                -> B4  -> B5 -> B6*
+    //
+    // nodeB chain
+    // G -> B2 -> B3* -> B4  -> B5
+    const { node: nodeA } = await nodeTest.createSetup()
+    const { node: nodeB } = await nodeTest.createSetup()
+
+    // nodeA will reject double spends after block 5, nodeB will always reject them
+    nodeA.chain.consensus.V1_DOUBLE_SPEND = 5
+    nodeB.chain.consensus.V1_DOUBLE_SPEND = 0
+
+    const accountA = await useAccountFixture(nodeB.wallet, 'accountA')
+    const accountB = await useAccountFixture(nodeB.wallet, 'accountB')
+
+    // create the chain
+    // nodeA chain
+    // G -> B2
+    //
+    // nodeB chain
+    // G -> B2
+    const blockB2 = await useMinerBlockFixture(nodeB.chain, 2, accountA)
+    await expect(nodeB.chain).toAddBlock(blockB2)
+    await expect(nodeA.chain).toAddBlock(blockB2)
+
+    // create the double spend tx
+    // nodeA chain
+    // G -> B2 -> B3*
+    //
+    // nodeB chain
+    // G -> B2 -> B3*
+    await nodeB.wallet.updateHead()
+    const tx = await useTxFixture(nodeB.wallet, accountA, accountB)
+
+    const blockB3 = await useMinerBlockFixture(nodeB.chain, 3, undefined, undefined, [tx])
+    await expect(nodeB.chain).toAddBlock(blockB3)
+    await expect(nodeA.chain).toAddBlock(blockB3)
+
+    // create a fork with a double spend
+    // nodeA chain
+    // G -> B2 -> B3* -> A4*
+    const blockA4 = await useMinerBlockFixture(nodeA.chain, 4, undefined, undefined, [tx])
+    await expect(nodeA.chain).toAddBlock(blockA4)
+
+    // continue the main chain
+    // nodeA chain
+    // G -> B2 -> B3* -> A4*
+    //
+    // nodeB chain
+    // G -> B2 -> B3* -> B4  -> B5
+    const blockB4 = await useMinerBlockFixture(nodeB.chain, 4)
+    await expect(nodeB.chain).toAddBlock(blockB4)
+
+    const blockB5 = await useMinerBlockFixture(nodeB.chain, 5)
+    await expect(nodeB.chain).toAddBlock(blockB5)
+
+    // now start adding the main chain until we reorg to it
+    // nodeA chain
+    // G -> B2 -> B3* -> B4  -> B5
+    //                -> A4*
+    //
+    // nodeB chain
+    // G -> B2 -> B3* -> B4  -> B5
+    await expect(nodeA.chain).toAddBlock(blockB4)
+    await expect(nodeA.chain).toAddBlock(blockB5)
+
+    // chain B should contain the nullifiers from the double spend transaction
+    for (const spend of tx.spends()) {
+      await expect(nodeB.chain.nullifiers.contains(spend.nullifier)).resolves.toBe(true)
+    }
+
+    // chain A's nullifiers store is corrupt, and is missing the nullifiers
+    for (const spend of tx.spends()) {
+      await expect(nodeA.chain.nullifiers.contains(spend.nullifier)).resolves.toBe(false)
+    }
+
+    // create another block with a double spend
+    const blockA6 = await useMinerBlockFixture(nodeB.chain, 6, undefined, undefined, [tx])
+
+    // chain B should not add it
+    await expect(nodeB.chain.addBlock(blockA6)).resolves.toMatchObject({
+      isAdded: false,
+      isFork: null,
+      reason: VerificationResultReason.DOUBLE_SPEND,
+    })
+
+    // chain A should not add it, since it is past its V1_DOUBLE_SPEND conensus change sequence (5)
+    // but it does because its nullifiers store is corrupt
+    // nodeA chain
+    // G -> B2 -> B3* -> B4  -> B5 -> B6*
+    //                -> A4*
+    await expect(nodeA.chain.addBlock(blockA6)).resolves.toMatchObject({
+      isAdded: true,
+      isFork: false,
+    })
+  })
 })
```
