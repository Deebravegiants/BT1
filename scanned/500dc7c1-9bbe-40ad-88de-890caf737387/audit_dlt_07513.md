# [?] fixes non-deterministic fee estimator test (#2550)

## Summary
Severity: Unknown
Chain: Iron Fish
Component: iron-fish/ironfish
Published: 2022-11-11
Source: https://github.com/iron-fish/ironfish/commit/6c9964fdee61d828034402ac3be4adc27407b2df
Type: security-commit

## Details
fixes non-deterministic fee estimator test (#2550)

a test is failing non-deterministically because it depends on the size of a
proposed transaction. depending on what order the account reads notes from the
database, the proposed transaction can have either one or two spends.

adds second account fixture and sends transactions to that account so that
account1 only has one note to spend.

adds test expectation that account1 only has one note.

calculates the expected fee from the fee rate and transaction size instead of
using a hardcoded value.

## Patch
### ironfish/src/memPool/__fixtures__/feeEstimator.test.ts.fixture
```diff
@@ -1195,12 +1195,20 @@
   ],
   "FeeEstimator estimateFee should estimate fee for a pending transaction": [
     {
-      "id": "f68e1a2d-0660-4beb-9f0e-35162ce46e7e",
-      "name": "test",
-      "spendingKey": "d4980f6d019d95bac58ee472ecd40c45f990876d3d1c17d1e2dc83ed5b721d72",
-      "incomingViewKey": "bb1054c4744d334b260c4118633681eb0d2ea08f00cacc6abf46b10b058d0306",
-      "outgoingViewKey": "abf9ffd47f86c6188364a5d9843195b66b7164dfb6b1ad707ba11c7e91d7e713",
-      "publicAddress": "d2338a30b37c40857800b13d2215f63f308c5939eddcc00201ed4e3650a9e67f99435f76552f74e8e2f21e"
+      "id": "505af5c4-b958-42a0-9269-4eb5510991bb",
+      "name": "account1",
+      "spendingKey": "78352ddbc29d74028589e11054f993455a56ae60bc9ceef942750e8bcd2a86f4",
+      "incomingViewKey": "0c4ed28702c5eef4bf12310c7a0298a927525038a6315ce92b429e8187a37804",
+      "outgoingViewKey": "c17ebc54ec13211af6ffb3f1fbde635915a60cbf9e76ec9bd258aa3ab2e21388",
+      "publicAddress": "e12b164844275b80ae4f2343acc27c1264fe90066cd8e77539bf017c69ed366826ed5d44e9fa1824e3aa1b"
+    },
+    {
+      "id": "22959ea6-2a8e-4576-978e-aded652c81e1",
+      "name": "account2",
+      "spendingKey": "d81853a1419f9bf98704d9f9214fe98e270696e261889524440e897b23a4a0c2",
+      "incomingViewKey": "774fe26e73bc6277cdcf65f49b2fb897221d515860e21f15fba9ad257d2cec00",
+      "outgoingViewKey": "498224f56e2e4acd26b30d35539a3cdbf2915ef8fe004467aae2ff1bd9641a6b",
+      "publicAddress": "ef3b3c401758da27ea5d4db73b4acebf4b6a5eb984a89df51360675fe117dec30f31eafd1793381c847d94"
     },
     {
       "header": {
@@ -1209,7 +1217,7 @@
         "noteCommitment": {
           "commitment": {
             "type": "Buffer",
-            "data": "base64:uB6zFN3aR4ePelP4Ds1huzCrLvFJTEPme3kIgyfz9zA="
+            "data": "base64:D3BNh3g/Y+1B2zXb11ssXLn5p5yXJTn5ZHsQUIl8ZD4="
           },
           "size": 4
         },
@@ -1219,60 +1227,52 @@
         },
         "target": "12167378078913471945996581698193578003257923478462384564023044230",
         "randomness": "0",
-        "timestamp": 1668120373074,
+        "timestamp": 1668125207726,
         "minersFee": "-2000000000",
         "work": "0",
-        "hash": "4AB5AACCD55997BF02D6961722AB8AE59C1E7DAC3CF60DA5E00CF659D30A10BF",
+        "hash": "27D43CC43CB706CF74E5C623E48CA952F7AF64FDC3B8A1EBBCA6A65B0179BA8E",
         "graffiti": "0000000000000000000000000000000000000000000000000000000000000000"
       },
       "transactions": [
         {
           "type": "Buffer",
-          "data": "base64:AAAAAAAAAAABAAAAAAAAAABsyoj/////AAAAALG/WWS4P14Jx1Ev20s80GmGu/NeHiqezVJrAfq5QBS8zTQmVmi+KhunKN7RN+GxxbfZQeZgUeGrmiAo/YVLbKmKMbSUTFD85ThPWFk85qdUuwbgSVs5xPSCd5GFQbatBAMbD9v8u1APqyNXKvdgaKogH7bn64/YkIRvAYOR9Q5s9Zt+2k6WYNQXTDJFW6Mora3xseuT4LaBdYH6/OM5T0TXthNxXuKXVs5y3ZyWiFS16ukmA99aL9jsT3UsiDmQLg93AOV2DV68kyZ0fr3H9fMfeVRJbmsxhZx9GaPJw6OFTXmsUgwyt43pQdn22B3lc4O5pmgXX5fWrtESoeZ1shRfqC4WK69GerTAnsfDrvFJyBGAGP8ZimwuxqNyO/I3jtD20xL8Uf52LaHWSvAp/FQVRV8Zz2K9eTMy5Hq2qRrrPZiBBYqkI/+VamJuyOFjGZ6174oKiFebZtMHWMK+Uifl1LHCS07L3kJ0p5aca3yGDY25MrH0nx8ko31a6UsNInpGSEJlYW5zdGFsayBub3RlIGVuY3J5cHRpb24gbWluZXIga2V5MDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwIe75JMsfwg58nEoaGyGa3dVUouXxjkhcrVBc9ca3kDkVIW+qr5u9Csf7wBTNl+ASJ7L4K+RiZRXRdPZa8f0KBA=="
+          "data": "base64:AAAAAAAAAAABAAAAAAAAAABsyoj/////AAAAAIn/S1seQakQ1ALos03gSXdN8LAl4wcXhe3bWh6tbBomHmoZD3tMzyMfZhjl7pi4NJFOEzT6LwhnymHGPwuQGhQDO68rVhfBdXWANjdjNS3O8rSCw/R4RgxDDNP0RYlZUQ2iJa7208ffw1tw61VdeRDdNYPH6x0LDX98/JPfTVA4Fg9gkGjxOPcq1U/fsmGIa5RVKTKsfp0TLVxWyZzRD3NwqBMnD8yKTvaO8LDJK2JNt+AoMrRj987TZwgZqb3em5ZmyaqS5bUOE589zjcNHSv4HktFMkHiQgcHQ8RkrW42xegthi8JuioTYOqzYMLMqYypXC+75F/11xLM7/QsyQ9+fQnmM/P0I36cI6dhnIRQc3sLwuqMMZJPOmX57n24PsSOMzIrzj7VBXvm/IUZlkHcOu7dutH+3KjE17h1XvIGqp8uDUFufFgfD9S/Xu0QW+kuXInv6YA3vtp/QEmyi3I5u/dHkujRXP9dYyc25rdKcWc3nhsAx5uyk9bCRCVrwix2pkJlYW5zdGFsayBub3RlIGVuY3J5cHRpb24gbWluZXIga2V5MDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwljAZdt8kOOL4R+SawrF161htwAqBVL4smF1sXTBD+QvGJO9Cy7tFI+NcOrsNraOwuD//1zrhagy/Cmd7GdfeAA=="
         }
       ]
     },
     {
       "header": {
         "sequence": 3,
-        "previousBlockHash": "4AB5AACCD55997BF02D6961722AB8AE59C1E7DAC3CF60DA5E00CF659D30A10BF",
+        "previousBlockHash": "27D43CC43CB706CF74E5C623E48CA952F7AF64FDC3B8A1EBBCA6A65B0179BA8E",
         "noteCommitment": {
           "commitment": {
             "type": "Buffer",
-            "data": "base64:Id6AlgKgilj7onz49MH9HpT0vu1yWGfijKaMK7pleD8="
+            "data": "base64:RNO0WVFGC0egAd7MK9yzsTLVkatsCr0QodVUcN1AG2w="
           },
           "size": 7
         },
         "nullifierCommitment": {
-          "commitment": "B9DD67FF7EDD7B50BA9E518AD7B88EA23A0812BB3A6D665C690D2A9E15E33198",
+          "commitment": "DC8B51715CDCA17216430BC1E4ED7F55665A344C388A6BBE40AD82C285B748A5",
           "size": 2
         },
         "target": "12131835591833296355903882315508391652467087441833704656133504637",
         "randomness": "0",
-        "timestamp": 1668120375481,
+        "timestamp": 1668125209914,
         "minersFee": "-2000000010",
         "work": "0",
-        "hash": "2EA428A947DBC95AA847DC5231804258FD5D07805D7C6651D47F84D7C1527B9D",
+        "hash": "D9DCC7A35BE75FC2899637183EE9010288452251A4C213A8FC2B8AC15C506C50",
         "graffiti": "0000000000000000000000000000000000000000000000000000000000000000"
       },
       "transactions": [
         {
           "type": "Buffer",
-          "data": "base64:AAAAAAAAAAABAAAAAAAAAPZryoj/////AAAAAISbgYrs/pTkd+oPzDxWUlwopmIb6uVGFOQJ8xnd6we+PFaAYPNbH9dNXF/FzC2g9KOgsoEvTdmF+bY/Qt8E3myrcjpd3vPKLFJtE63fLqwkwsrxZdmgtN4eZb6b9tyCuRZKG9jJrI5bspU/2bIHt4sQnRViZbxWtK5R/MhtruA/+5oui8EuNI/q59NdWHhciYjor5lDFDy/KkkFg1KIpOX8STmt0cDQ76O354tJIuCjk/mwBuWtSNcj12P3TCiCPS8ayXMjB3J4tb+JdxeLCdeG2004TJAKuXLn2q32eOmBxYOntM7lC7grqV8FYxUnmCtYdqBiNshm/DTT2R9YmW+NQDlMEXEWHbFiMa51j8CwRLU5AHA5f09Wi46OlTLZhtgMsXbks1uTfhO/OSFw7AZ68tmZQVTuhIOu0TlmHWGAt7lutlxJUxmkNh1xjw/8hgWPNcQ9QAznVez4WC/JrMzFB/1+mypYr7gVqncK0KP/PhrDTAVYzsOLT+wIPrIt7xd6PEJlYW5zdGFsayBub3RlIGVuY3J5cHRpb24gbWluZXIga2V5MDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwJ8MomltJbXlfANU0hI8dCKwEIPuFLtiQSY2o6imZwW6T4WjVtBelrmL0jYGfXIl/+RWj2XkrvMJzFP4YxLLwCw=="
+          "data": "base64:AAAAAAAAAAABAAAAAAAAAPZryoj/////AAAAAJhx5Zsc/GF1UgRynmAQ6gBqpSWYaTDU7VD4gMEpAYD1spx5Uxg+AoypLQuDaorhNbYw9NQB2FInxbKJXtWCnh/bnpNqhuK6gC/T9adfbyu9X1VSqGNgUCG7h1qBTXsSxhJknmZgd60XAvUFmnG1HwwkdoVEtR9zJ+E0FNQTBQ2l0iwdtqTUpHVomk8e9kFft4S8Z3S7eUNhYeldVd+SJxjcq4R3PfhTJukaqdOBRb+o/om/3A62TEEsKTB6NnIah32gAZ5AFDBZ/cZH0/+GodAMcLRIZiaAlwT74vzL8kkp6voiU84AnSymhR+EK2Ef35y/xxswesmfBTofTsanxShBOq+r6bhTvVwC0Ajovhu96pc+CaadLugjDjuz7uP5ZLKa+pVLH/BtKITTD3jLMU+7yZHwSd26m9IkGZnLebGNTIkdC/mqhQEPAod94pep+srFzdERkTMLGp4DgxvMUMUOfktg0XkJHMkbQNvPA+K/6U7tWZld3/4v7pZ63OyrhsvYj0JlYW5zdGFsayBub3RlIGVuY3J5cHRpb24gbWluZXIga2V5MDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwNFLnPTSHbiidQXXKT5HkRDmzMj6H5pZSDDK9Rf05zxn0Xc5CkVbPLAa9UWTrEaK1dUO5QMPfuLFH8DRlZF25AA=="
         },
         {
           "type": "Buffer",
-          "data": "base64:AQAAAAAAAAACAAAAAAAAAAoAAAAAAAAAAAAAALb6hmvI+P4piBwn5E+Td3/Z6rA1WgY5HYVZRT2njF/N3WSe9ro4wZR2a0TWInYoWIVXTHQegnTAPY95mPSctoazIv/m2Bt1Mio1V9yg8wYtTo/S0L97bTrCqB+Ba0URzxH5Bb/+CBmArQujIrP8oRRlkuAeDvk1g1+9GyuRnYRwdR+bRGV2lN0aJFOTyAX3pLmttkcatlarkbn17mXn2vp+Em/U8EfIrmvpmBl4zNa01SiZutMIbpkAKn1hfG0pUO29qK1nXzi2duGaKMPqUXzx9rrwqfk7f3hEyV7oM/LHCrhPm/NK3VM8f/Hikuw8BwkqZh791sWWbBkGXJuJ4li4HrMU3dpHh496U/gOzWG7MKsu8UlMQ+Z7eQiDJ/P3MAQAAAC//A4L8ijun83QWChiHeSwBCPA5zjwu4AKQccv3bdmN3bp0W+81UgnlUN8y6yUS25JJ5NbdxLN+TrJylopgDWxgQ3u2tQW5JEjmX5/Z8IsiI64Cd0JPbm3lOrYPQyOaguHgMjaQ1TNN83UqHyZ2EmDW65IvA/GCF2MFh2lsqRjVmvvpbb3u+x4S3dQ3jY3KUWudgX3ROpAG99fqXx+SY2en+QT+v5LmdJV5iBURD5qYqJ/iMYTyXELSO46mF8DY44KtDsbBUAefeCpLJgEoSzn/ebCLbVhullC5qm/Eib7VjVDO/tAVKIdEyCqKO272jaYt/jVC+BQ6B/DsQlXTNmoG721jcosEUcqfXB0W8E7tle7mcdWSN8sh9JNTt50TrzFU0EMCdmN1SOsiwihhec8Y0eYPhpnK15XxEphg8YnnspFGAJoLh6Y33bTzFNJcYDdAiI/DpSKcC5uz2OukpZAmCGLRt3LebS0gmkW7YozGp/+Jrc34K0xJ3YhJV7nrCBAfZs++O+pbUrVqKuite2po2g7Hhx1dBCr6zWlE3rDKEWqV1RV3YapvAUhHC895zcXEwd2P2qYcR92AGYjRjYp/mS66pDb31jLgsRiRAI4htPyzhLzD/lvtFX3BWOzxFnvxSyUO3Fyc872b1rxRwB05wCel956wDAYy336KU7ZF3YGtsh6FEjVUjzttX0V43FE8Uh1Hfmmb88qn2ue2E39i/eXLta/yhHw7qHSSHQ2t9lGgK6zEE0HvdT2xLfh4qRgIc1mAJH/7jpGHXJYVu9m1xXipCQcNfSM1KF2V3yjoPgJBZTz+Bj2wTNwgnqijeClJIpXIq43q3ci6CFmfnDEwj93q2pENlPyc4rz7fCvwsZDtAZkwaVP4yJS3PnhOw+ul6gd1rxQcK+u5QW1aq9VFf580bnU7JJBO89UlT9h5Ki7aI9RSJfnuxUg+mVJ1/oJWx4Cq0ITPcGLlR+oriUFhFgjPFPzIkmrMWL57aXu0vaOh9G8yKhpdFmwvn3aeRREuiU/pCCNrNJkRWG3/v43Cag446W2ntHAsZ+XZOYF98oUKfi5IDpvdQBv6IxJ3MowySyHgHqheBkEXssvzNnQGplNuueM5+d14FFSKEd3T9ZKnozpcPSiDmXTifDQIjtH5qhyfFXhiY109obyzCZcfDsEosbUalutp2h6Y35AiNjucq06MHcYk7MfYG+KHocGjbsQ9l0RgFd6PaYsqVQtkEHbL0Ksu/OC3vvHdlv63UeNZR5Lorl3/h2S9sgwqiXCTpYWljbm878wEycUu5Q4T/teXHnAGAtcWFvNUBDFhhzjqcxbqJwSWSj7NMJU+ACijzvWvszMmbGX8RCMCH2y3Vs/Wd2Lg6anKHvaANNFr/yDfeoVcZrUK27t3tYkTjs70lpFcgaQYMdyso+pFKGTfQIpL4UM5mVBRX8kWg6KkXG/P303Bg=="
+          "data": "base64:AQAAAAAAAAACAAAAAAAAAAoAAAAAAAAAAAAAAKw0OxV72suDV4mU0UePkonNAnJURrCHAUSZvie4eBJhufShRrQcV4Sbf3Ttfuy9dYMjspLC2sIMU2kPKMDDn+llvPbM+fmamCmcIUxuNUQCgmog+q4w3zjnB3dfP5kPJA2Ac3WJOJUJxYB4CYHEF8uaXwcsQP/MXFluq0rDZpNfbzbb5smP8bRHEMXwiZxXFY36hEGJhmTmeXWcqwxzHUsqboeXXWxxmxgrjutoFGVaPShFDXcCvaKADO6uJH1XICVyFTNXRdmoT99CbXQzMmFXs9zyrEoPFCuLr5t9oQ6DTMHzDpSsPLK4KV2S9oIJ2cT908iLlrIqumv20mM6LuAPcE2HeD9j7UHbNdvXWyxcufmnnJclOflkexBQiXxkPgQAAADFxzULspMGAHuWn36ZU7hu+VfmszbFWP0inyOOYlOB4iYddFlWZ469r1vEOJcupIvmpqfedFRaYQVKs5KM3h1XsMvNY02y0849n3okM6H1oO+FXfyH41NOXKUN5/nd6weCoRstM+mNB0FT44KSGt6lGB4jSSBzCG+q9Jr0W/2hVmAqNf+MUntfYuOseis+bEqWkacPoCQijUEtcYprwj0QR/YzPL5qXgWcQGeuAqN3PqLQOIsM3lMvUxaHv8DA8C4CWnmuq7vqM968kXl3TB05P/HlsUEYCiEAQlvuDkKlK+QBL0mFZNBPikYNuazX1hS0QyOW3ScuPCrAMNoskrNSx27GSk1fQv7h8DTLXuxncybg7B2l9IFw87QcW1pkzS8FrBD6Qp+MmnRw54L8jXQYWRfobiiB1WkfsRHuliqF73uypAM5pMoR1kSvBZWkKsueD9CtGYFXQoyUBKqL7nNepua/GTVnKtTgjL4ZlOFV2Q2Io5ovE8LvLO/nK78Mcj1/pmc6ibWBGgpKj9s4NwxOOBqPYS7dSwhGRvHAbKzV9x0eK6EkRJGgfpHkWwIlqdNzEaZPn8TNp2vtuC09Mn8hQEJ7G43R8s6tGSi7qZDIlN3UMrh0zZ3g3PRMPiHCWlYzqdYtLpZFIpcHxtH4UFESbjjcoLQ8mn+waQg/sgvVzH8cMGFdsHBN9obeqFVE2K4A4R54+ovR9Is7HHzM7iSfSjwFW67oyFgyCQPKHQVOEcXnN4hPHS+r1P49mSRdPTaMosmGqRTr+P/n8wrXT3CRDX67uAZw3WQtMI8iXNyuP2Tzvo/kOH+RkTRnaqmy8iw95mHdNHALw+G+Lcgrfd/KgA0Ysk7h2OqV+3JVE5lWDcIXjQuLG1XybqRXTNLQBdpXc6N1qvlx03DSYTobM90FHVHruay3fnPiWy3sgNZTV6TQlIx+ypCgVYwTcsuOSSm/yA+Z7SrThwgKIDRveBHhN4/dnf/SgeWafpa12kVYxPOQM7Dq7hPghzgfEntpFBgtK+bF4UMFai2fKiFdYTJ2YWnjctprhdOHk/SbgKvQtsU5FzlpjKbMGhlrVRqHL8FODm4fLD4hiuW3pO4h9i3DdfOTx6aQnR8ev8fVHP9yh4UonT12NGC8c+mqXTbtfKziJlUJbsbgH+abug48r60JJ6FknIqQ3ijeWMTwYqdzzneHZJ/1wG7Z8oO/shKv2KFaDsEQP8IHaSvHFHPdb7AtddMRVBEB4Hjg0AooqvT9xNPE1qTfN1zo8/3PUOVfWAr6Nd48qI4WSaFrHmBaKJr1E2TGxXLtlwK5zqHoxiB8Cn0bGJ7GvZPRj9SdCStqo7hkDpDDrrpkTcZokHp6ja1bsioLU0Wx4FWn2ThmrwcAHORj+OrHOZ2J5Fdk1EKAgKoAh5hJk7g0tZVuBk066I5nDk975AmQGwKx8Y/WmL8o1j4EHyG2CQ=="
         }
       ]
-    },
-    {
-      "id": "be7940f6-dda6-4750-ac91-783b61cf013f",
-      "name": "accountA",
-      "spendingKey": "c040c58b8289a2801cbf4202cdedbba7428298cdc9bbf5d8212bd48c838ac9be",
-      "incomingViewKey": "a9e54c687d82dc7bb66228cd49903fb3e313ab6ad40230a36a4cc5dde50af006",
-      "outgoingViewKey": "9f5ccf8e800989b576e8dd11eb25d7411a029c1bb70201fd5f59dd0589126348",
-      "publicAddress": "5e8785170aff71c724c4ae5a9c31ba0bca5348757a42365d417e7dbd0773ffba05deca075d65496e181ceb"
     }
   ]
 }
\ No newline at end of file
```

### ironfish/src/memPool/feeEstimator.test.ts
```diff
@@ -2,13 +2,16 @@
  * License, v. 2.0. If a copy of the MPL was not distributed with this
  * file, You can obtain one at https://mozilla.org/MPL/2.0/. */
 import { Assert } from '../assert'
+import { NOTE_ENCRYPTED_SERIALIZED_SIZE_IN_BYTE } from '../primitives/noteEncrypted'
+import { SPEND_SERIALIZED_SIZE_IN_BYTE } from '../primitives/spend'
 import {
   createNodeTest,
   useAccountFixture,
   useBlockWithTx,
   useBlockWithTxs,
 } from '../testUtilities'
-import { FeeEstimator, FeeRateEntry, getFeeRate, PRIORITY_LEVELS } from './feeEstimator'
+import { AsyncUtils } from '../utils/async'
+import { FeeEstimator, FeeRateEntry, getFee, getFeeRate, PRIORITY_LEVELS } from './feeEstimator'
 
 describe('FeeEstimator', () => {
   const nodeTest = createNodeTest()
@@ -382,30 +385,47 @@ describe('FeeEstimator', () => {
   describe('estimateFee', () => {
     it('should estimate fee for a pending transaction', async () => {
       const node = nodeTest.node
-      const { account, block } = await useBlockWithTx(node, undefined, undefined, true, {
+
+      const account1 = await useAccountFixture(node.wallet, 'account1')
+      const account2 = await useAccountFixture(node.wallet, 'account2')
+
+      const { block, transaction } = await useBlockWithTx(node, account1, account2, true, {
         fee: 10,
       })
 
-      const receiver = await useAccountFixture(node.wallet, 'accountA')
-
       await node.chain.addBlock(block)
       await node.wallet.updateHead()
 
+      // account1 should have only one note -- change from its transaction to account2
+      const account1Notes = await AsyncUtils.materialize(account1.getUnspentNotes())
+      expect(account1Notes.length).toEqual(1)
+
       const feeEstimator = new FeeEstimator({
         wallet: node.wallet,
         maxBlockHistory: 1,
       })
       await feeEstimator.init(node.chain)
 
-      const fee = await feeEstimator.estimateFee('low', account, [
+      const feeRate = getFeeRate(transaction)
+
+      const size =
+        8 +
+        8 +
+        8 +
+        4 +
+        64 +
+        NOTE_ENCRYPTED_SERIALIZED_SIZE_IN_BYTE +
+        SPEND_SERIALIZED_SIZE_IN_BYTE
+
+      const fee = await feeEstimator.estimateFee('low', account1, [
         {
-          publicAddress: receiver.publicAddress,
+          publicAddress: account2.publicAddress,
           amount: BigInt(5),
           memo: 'test',
         },
       ])
 
-      expect(fee).toBe(BigInt(9))
+      expect(fee).toBe(getFee(feeRate, size))
     })
   })
 })
```

### ironfish/src/memPool/feeEstimator.ts
```diff
@@ -171,7 +171,7 @@ export class FeeEstimator {
       receives,
       estimateFeeRate,
     )
-    return this.getFee(estimateFeeRate, estimateTransactionSize)
+    return getFee(estimateFeeRate, estimateTransactionSize)
   }
 
   private async getPendingTransactionSize(
@@ -195,8 +195,7 @@ export class FeeEstimator {
     size += receives.length * NOTE_ENCRYPTED_SERIALIZED_SIZE_IN_BYTE
 
     if (estimateFeeRate) {
-      const additionalAmountNeeded =
-        this.getFee(estimateFeeRate, size) - (amount - amountNeeded)
+      const additionalAmountNeeded = getFee(estimateFeeRate, size) - (amount - amountNeeded)
 
       if (additionalAmountNeeded > 0) {
         const { notesToSpend: additionalNotesToSpend } = await this.wallet.createSpends(
@@ -215,12 +214,12 @@ export class FeeEstimator {
   private isFull(array: FeeRateEntry[]): boolean {
     return array.length === this.maxBlockHistory
   }
+}
 
-  private getFee(feeRate: bigint, transactionSize: number): bigint {
-    const fee = (feeRate * BigInt(transactionSize)) / BigInt(1000)
+export function getFee(feeRate: bigint, transactionSize: number): bigint {
+  const fee = (feeRate * BigInt(transactionSize)) / BigInt(1000)
 
-    return fee > BigInt(0) ? fee : BigInt(1)
-  }
+  return fee > BigInt(0) ? fee : BigInt(1)
 }
 
 export function getFeeRate(transaction: Transaction): bigint {
```
