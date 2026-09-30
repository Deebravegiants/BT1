# [?] flamenco, cpi: fix memory corruption bug with allocating instr infos in cpi

## Summary
Severity: Unknown
Chain: Solana
Component: firedancer-io/firedancer
Published: 2025-03-21
Source: https://github.com/firedancer-io/firedancer/commit/f35407b68d2db3f892707dbc02025e60b2a1242c
Type: security-commit

## Details
flamenco, cpi: fix memory corruption bug with allocating instr infos in cpi

## Patch
### contrib/test/test-vectors-fixtures/instr-fixtures/bpf-loader-v3-programs.list
```diff
@@ -1,16 +1,17 @@
+dump/test-vectors/instr/fixtures/bpf-loader-v3-programs/0ca71524409b368d3626cf1927c61ce10dde6f09_482318.fix
 dump/test-vectors/instr/fixtures/bpf-loader-v3-programs/13edbb5660baa6c77f48f77f3239e2a1210c9aee_146798.fix
+dump/test-vectors/instr/fixtures/bpf-loader-v3-programs/1848e2dd264685985f742e69e7f676bab4a9c1c2_1500689.fix
+dump/test-vectors/instr/fixtures/bpf-loader-v3-programs/33258035450143403fc216e966c799f4e505f879_1638849.fix
 dump/test-vectors/instr/fixtures/bpf-loader-v3-programs/33eab234782af2476a353410d8d15949ec5564c3_452715.fix
+dump/test-vectors/instr/fixtures/bpf-loader-v3-programs/3be4abab230b401c2008cebfbad60962b30f6854_474559.fix
+dump/test-vectors/instr/fixtures/bpf-loader-v3-programs/40485bbf533af92715288ace8a94001d8ccd1a6f_1689236.fix
 dump/test-vectors/instr/fixtures/bpf-loader-v3-programs/4c3874406b6bc014434a6b08cfd7ce957005c299.fix
 dump/test-vectors/instr/fixtures/bpf-loader-v3-programs/572bef775bfe039859f9ba7765452b8c0167548e_684111.fix
+dump/test-vectors/instr/fixtures/bpf-loader-v3-programs/5a4fa99bd1c91cd4b9f86705bd9971c1db1ce951_490900.fix
 dump/test-vectors/instr/fixtures/bpf-loader-v3-programs/6eba3d3dad89e309c3e2d82c1262ed31a8c350ea_611631.fix
 dump/test-vectors/instr/fixtures/bpf-loader-v3-programs/7f4fc5e74294d1186904d8c5eada3dee2cd657db_113648.fix
+dump/test-vectors/instr/fixtures/bpf-loader-v3-programs/9ba48219b4ef2a690de9dcc2e240bc2f70c4f4f3_2587490.fix
 dump/test-vectors/instr/fixtures/bpf-loader-v3-programs/a03f65227ebf67c78a38545ae70def1abda85b9e_468266.fix
 dump/test-vectors/instr/fixtures/bpf-loader-v3-programs/crash-61560dca014f17632760e7915b271cfba4fdb121.fix
-dump/test-vectors/instr/fixtures/bpf-loader-v3-programs/1848e2dd264685985f742e69e7f676bab4a9c1c2_1500689.fix
-dump/test-vectors/instr/fixtures/bpf-loader-v3-programs/40485bbf533af92715288ace8a94001d8ccd1a6f_1689236.fix
-dump/test-vectors/instr/fixtures/bpf-loader-v3-programs/33258035450143403fc216e966c799f4e505f879_1638849.fix
-dump/test-vectors/instr/fixtures/bpf-loader-v3-programs/0ca71524409b368d3626cf1927c61ce10dde6f09_482318.fix
-dump/test-vectors/instr/fixtures/bpf-loader-v3-programs/3be4abab230b401c2008cebfbad60962b30f6854_474559.fix
-dump/test-vectors/instr/fixtures/bpf-loader-v3-programs/5a4fa99bd1c91cd4b9f86705bd9971c1db1ce951_490900.fix
-dump/test-vectors/instr/fixtures/bpf-loader-v3-programs/9ba48219b4ef2a690de9dcc2e240bc2f70c4f4f3_2587490.fix
 dump/test-vectors/instr/fixtures/bpf-loader-v3-programs/d9df3ffda1439f09ab7234f0846cf0f5fee3d15c_2587609.fix
+dump/test-vectors/instr/fixtures/bpf-loader-v3-programs/instr-Sz5UjeMULjCMyvctj8537vMdk3q44To3BjeFpi5PBFZowQWJMmZXQw6VUEJBDCMaE9m4yEnVQCMhqYgp1T5vQea-003.fix
```

### contrib/test/test-vectors-fixtures/txn-fixtures/program-tests.list
```diff
@@ -374,6 +374,7 @@ dump/test-vectors/txn/fixtures/programs/1f87f98c3005f5cd444bcacf17b44ed360b23187
 dump/test-vectors/txn/fixtures/programs/1f8baa7cca9a50f2a30d2a23bf19de90f4130c01_265678.fix
 dump/test-vectors/txn/fixtures/programs/1fd6fbf850d414f13cabb18b7f265b7718e2afb5_265678.fix
 dump/test-vectors/txn/fixtures/programs/1fe88a97c6185afd668574ede8b54a764a86f090_265678.fix
+dump/test-vectors/txn/fixtures/programs/1fff2d993f4d7677640b2b3397320496b076e854_3506222.fix
 dump/test-vectors/txn/fixtures/programs/201819d6ca202d1cfc7e2debabc40ecec9c52076_3616547.fix
 dump/test-vectors/txn/fixtures/programs/2018a056247847735df7ae86d5324eaabc98525b_265678.fix
 dump/test-vectors/txn/fixtures/programs/203168869dffe554988214b92c84ec169868c52f_265678.fix
@@ -399,6 +400,7 @@ dump/test-vectors/txn/fixtures/programs/21c7b8d33a3f3e20e2f8e67947f1abab02fe3b78
 dump/test-vectors/txn/fixtures/programs/21d3e47382275796116f3221d50c5e81e28bfb7a_265678.fix
 dump/test-vectors/txn/fixtures/programs/21df17c47c8c2a346b816d7a0d898a1a572cc11c_265678.fix
 dump/test-vectors/txn/fixtures/programs/21edb130cead1eb3c8735a91fc6847d3aff98e30_265678.fix
+dump/test-vectors/txn/fixtures/programs/21fb4857674201e9f6c173c1f2e83556718c401e_1556049.fix
 dump/test-vectors/txn/fixtures/programs/220d744a8d5a99966e798dee6f7df3bd5f0c6b14_265678.fix
 dump/test-vectors/txn/fixtures/programs/221f3a78a164e7c1590b409f6f41d3532d0dc4fa_265678.fix
 dump/test-vectors/txn/fixtures/programs/2230308262f87f9091245451f491ac8a95b03d5b_2913590.fix
@@ -601,6 +603,7 @@ dump/test-vectors/txn/fixtures/programs/336d02418733429375c66974ec716d58d27cf790
 dump/test-vectors/txn/fixtures/programs/336d88c28a052cc92cd11d457ceb1cfb78f2102e_265678.fix
 dump/test-vectors/txn/fixtures/programs/336dc1ba24cd51b0ca26eb4c7fde8afba73791b8_265678.fix
 dump/test-vectors/txn/fixtures/programs/3387990b332870b2f605dd249f0b7ea90c0e1a82_265678.fix
+dump/test-vectors/txn/fixtures/programs/338a0b377eb143b9d2520fd81d6b8658ea71d32a_1183730.fix
 dump/test-vectors/txn/fixtures/programs/338c3650424513fa6796d3d9a24a16c3b0343901_265678.fix
 dump/test-vectors/txn/fixtures/programs/33998246ed4afebbf42883c4f56d44a1582cc9e0_3205875.fix
 dump/test-vectors/txn/fixtures/programs/33a22acae9903d260fb964f8645ecbddecc68cd5_265678.fix
@@ -815,6 +818,7 @@ dump/test-vectors/txn/fixtures/programs/4592bdeb3356c06651fcdfe0ee40c4ce062c2f12
 dump/test-vectors/txn/fixtures/programs/45b7cb9916efaaeb3841ca263a5e4b8b21669a23_3005855.fix
 dump/test-vectors/txn/fixtures/programs/45c05d2343fb18aa76a73e0f654a688e54230595_3541699.fix
 dump/test-vectors/txn/fixtures/programs/45dbb4a94756d89f253b000bd83483825efd8041_265678.fix
+dump/test-vectors/txn/fixtures/programs/45dd4971a31ae58798211458d14551780be22c7a_1633256.fix
 dump/test-vectors/txn/fixtures/programs/45df673986eab65a67dd740522d69ca2ded3dc0c_265678.fix
 dump/test-vectors/txn/fixtures/programs/4604704f1c55157bfb4cd54e794788d21f0308ac_265678.fix
 dump/test-vectors/txn/fixtures/programs/4645c14237860c4b4c7dfc1b6cc8932b46330271_265678.fix
@@ -1509,6 +1513,7 @@ dump/test-vectors/txn/fixtures/programs/8029019bef598bf123b72cf81d27eeee6c9fda0f
 dump/test-vectors/txn/fixtures/programs/80495f7bfc9e4563f9d56e837692737abb91d636_265678.fix
 dump/test-vectors/txn/fixtures/programs/804fdaac18982bd63eb28a0a75ff5475c376116e_265678.fix
 dump/test-vectors/txn/fixtures/programs/8058bc025a4501d8188c291b08bbdc780591cda3_265678.fix
+dump/test-vectors/txn/fixtures/programs/805e0cd05df6ceb015a08086e9bcfab51f559747_180823.fix
 dump/test-vectors/txn/fixtures/programs/8061f4b3293830badf653e04d0eb738f1384d4b2_265678.fix
 dump/test-vectors/txn/fixtures/programs/8088ba17dd927644df610f9aed54ed407632556f_265678.fix
 dump/test-vectors/txn/fixtures/programs/808d39cc6a9ffa50ee681e0cef7aa280729f9e68_265678.fix
@@ -1555,6 +1560,7 @@ dump/test-vectors/txn/fixtures/programs/84a2bdae31184ce6301768b38d0ff020dadd1411
 dump/test-vectors/txn/fixtures/programs/84cb4e0e3348ee4dcad2cff5f19127d5db57aeb8_265678.fix
 dump/test-vectors/txn/fixtures/programs/84e5948d880e89052b3ccb610737975247b34fb7_265678.fix
 dump/test-vectors/txn/fixtures/programs/84f114b17587f88281f867b17a95ec4a8118f620_265678.fix
+dump/test-vectors/txn/fixtures/programs/84f3a1500cd82eb29554c49640400e9d96783dc6_2395779.fix
 dump/test-vectors/txn/fixtures/programs/850384bbd4d1b8c25de0c7516cc4b823801ee570_265678.fix
 dump/test-vectors/txn/fixtures/programs/8509b79cb4680520df6d470cef60d57cb015acd8_2468211.fix
 dump/test-vectors/txn/fixtures/programs/851b6103c949da132a384ec02537b25b92c10390_265678.fix
@@ -1645,6 +1651,7 @@ dump/test-vectors/txn/fixtures/programs/8b8cddcfac052744630d7eb767455117639d2f3f
 dump/test-vectors/txn/fixtures/programs/8b942803e7d4376d463b9f496a5b434f03dad5df_265678.fix
 dump/test-vectors/txn/fixtures/programs/8bbbe211511655073656ce6359539e547980fda9_265678.fix
 dump/test-vectors/txn/fixtures/programs/8bc6bfb40f1d4d259f2802ffda0311a7a7c0ad26_265678.fix
+dump/test-vectors/txn/fixtures/programs/8c00535b747c262681aa014f688dafb22c34546a_1631431.fix
 dump/test-vectors/txn/fixtures/programs/8c0ff72478b714502fb21e21c0e5b114a643d5b7_265678.fix
 dump/test-vectors/txn/fixtures/programs/8c2694ca2aadd09625e60dfb1d952ad475c1c853_265678.fix
 dump/test-vectors/txn/fixtures/programs/8c2727ef5eba21323bf14216dca3d1527d09b255_265678.fix
@@ -1996,6 +2003,7 @@ dump/test-vectors/txn/fixtures/programs/a9f37c82a25b385e2a305d224bb9d11525245e6b
 dump/test-vectors/txn/fixtures/programs/a9f900d56a144f808d7460c739a2072fb461f167_148681.fix
 dump/test-vectors/txn/fixtures/programs/aa2aa35ce3efe0691ce79258f6d2b22141fc709e_265678.fix
 dump/test-vectors/txn/fixtures/programs/aa3034f397fbe6fee7c85019213330e7ec7bc217_265678.fix
+dump/test-vectors/txn/fixtures/programs/aa41354131885b471f301100e5a614a16b21cbc4_3139208.fix
 dump/test-vectors/txn/fixtures/programs/aa49773a86c302586bd51d6b96f2e5a4f7b8e2bf_265678.fix
 dump/test-vectors/txn/fixtures/programs/aa4d442af33d0d93e52db2e0347dd2b79bc2262f_265678.fix
 dump/test-vectors/txn/fixtures/programs/aa7eec20d7a0acc588bb07c486537fc32a5b63fd_265678.fix
@@ -2015,6 +2023,7 @@ dump/test-vectors/txn/fixtures/programs/ab9bc437a539f37fe6956bcb479c17fec7370b73
 dump/test-vectors/txn/fixtures/programs/abb78d67141ff4ada8d4b5cdb4c59d5df1352f41_265678.fix
 dump/test-vectors/txn/fixtures/programs/abbf8109e4ede5fbd0a1079d195314ff927c275c_265678.fix
 dump/test-vectors/txn/fixtures/programs/abc0664bbd021d14eba2c9eaa0e192dbca74f060_265678.fix
+dump/test-vectors/txn/fixtures/programs/abd3e18d9c1672c7ab644be17ae30c921e72c4dd_1631283.fix
 dump/test-vectors/txn/fixtures/programs/abd602c02af29809a0066c80dc5e7b61e9388e58_265678.fix
 dump/test-vectors/txn/fixtures/programs/abe27fb52854fa72463de17307d83843d1718333_265678.fix
 dump/test-vectors/txn/fixtures/programs/abe679e3bf4f8dbe36da22f126dbf284a14e8f3d_265678.fix
@@ -2121,6 +2130,7 @@ dump/test-vectors/txn/fixtures/programs/b58fd1189fde031f8473768170db3d11e56ec7a8
 dump/test-vectors/txn/fixtures/programs/b59bb607a0f26815c38e7c0f47c5eaafb01f18b0_1576002.fix
 dump/test-vectors/txn/fixtures/programs/b5ad97d8314a28b7f812a6a647b7729d458dccd2_265678.fix
 dump/test-vectors/txn/fixtures/programs/b5ece7ce4804f4c6494578208d227f710574e29f_265678.fix
+dump/test-vectors/txn/fixtures/programs/b5feb69c36929915f3d24aaa79cd5786eee5aad7_1047123.fix
 dump/test-vectors/txn/fixtures/programs/b607f29af8977a27cc7451d0969698eccaaa2d48_265678.fix
 dump/test-vectors/txn/fixtures/programs/b6551334512ee7238c557f06cfad3fbf55bf9695_2243607.fix
 dump/test-vectors/txn/fixtures/programs/b66640fd98db92bc3400ceb680b901a2c3dcc9a9_2371788.fix
@@ -2154,6 +2164,7 @@ dump/test-vectors/txn/fixtures/programs/b8a7eb1afb52da9baa95f6c6260ae82de0ce0fa5
 dump/test-vectors/txn/fixtures/programs/b8b1bef546bada12e4fb42444b34cccb7c700b7b_265678.fix
 dump/test-vectors/txn/fixtures/programs/b8dbda1d6036163e8686f273c50f7e7d79c9cef0_265678.fix
 dump/test-vectors/txn/fixtures/programs/b8fe06153971fe59b387ccc1aeb7ad36e7065cd5_265678.fix
+dump/test-vectors/txn/fixtures/programs/b91c038fe6bc76b330f4ae8719a9e8c47a8d28ed_434577.fix
 dump/test-vectors/txn/fixtures/programs/b91d9dda2c6216a6761f09b13483d120f1e42024_265678.fix
 dump/test-vectors/txn/fixtures/programs/b922d80c9abbeaa80b08d333ab031a65ea2f2767_2997144.fix
 dump/test-vectors/txn/fixtures/programs/b95602a274d92106dacd2f1d0f22d6ac4c94d9fc_265678.fix
@@ -2273,6 +2284,7 @@ dump/test-vectors/txn/fixtures/programs/c2b2968bb09dc71bf2639298b41e86ba0d187850
 dump/test-vectors/txn/fixtures/programs/c30f224e9a30678643e784cf1fa996b14f541fb3_1561270.fix
 dump/test-vectors/txn/fixtures/programs/c31731da0337a24b817c63ccb9ee1f7ecac43e32_265678.fix
 dump/test-vectors/txn/fixtures/programs/c325ff81d6c902452d66d8d35664a2f45f1411de_265678.fix
+dump/test-vectors/txn/fixtures/programs/c3319fc3a5c525a7612fb139ddd49862e01fd909_2766868.fix
 dump/test-vectors/txn/fixtures/programs/c33210dc671fe650e635d5a6027fc364a0c640c4_1961775.fix
 dump/test-vectors/txn/fixtures/programs/c33402910a3dde1519f3c53b8d9ea566f08fe59e_265678.fix
 dump/test-vectors/txn/fixtures/programs/c35a88f04e641beb3d65847952da7ee66b808a95_265678.fix
@@ -2368,6 +2380,7 @@ dump/test-vectors/txn/fixtures/programs/ca7e6931dcffa08db8e9e2ee8060d09d1c94359e
 dump/test-vectors/txn/fixtures/programs/ca87cc94b69bcda9a032cb1a91864ec07bd88307_265678.fix
 dump/test-vectors/txn/fixtures/programs/ca87e31c6c9094c86c28c3d690424ce26ec05099_265678.fix
 dump/test-vectors/txn/fixtures/programs/cab09a11d027117f1e62ab93f8ebda0be4498f7e_265678.fix
+dump/test-vectors/txn/fixtures/programs/cab41c4453c9760b32a6015be5823cce3750b032_2009105.fix
 dump/test-vectors/txn/fixtures/programs/cac611f2933c12018849200153b147ceecf383cb_3220725.fix
 dump/test-vectors/txn/fixtures/programs/caf25695d303f2db08544113a2ef5f6b2b9eee96_265678.fix
 dump/test-vectors/txn/fixtures/programs/cafc486a820fe0683c588e3defb5daab7a21a707_265678.fix
@@ -2529,6 +2542,7 @@ dump/test-vectors/txn/fixtures/programs/d62c274c46f26fe100cfc414266742d0749ae9e2
 dump/test-vectors/txn/fixtures/programs/d62d20132c6c40393582ac1c08cc9806b8373111_265678.fix
 dump/test-vectors/txn/fixtures/programs/d6644312b1b53f4e870f12331edf4e72d35eb963_265678.fix
 dump/test-vectors/txn/fixtures/programs/d6739eca1f83d7264ee08249450b894b9ca9e253_265678.fix
+dump/test-vectors/txn/fixtures/programs/d67f442716145cf5645900048f5d35466cc88ac5_1631585.fix
 dump/test-vectors/txn/fixtures/programs/d6b948e109e3acb27c7a4bed7de32220ec008de5_265678.fix
 dump/test-vectors/txn/fixtures/programs/d701757011399fb1931ec091e274b3ec98918632_265678.fix
 dump/test-vectors/txn/fixtures/programs/d70756e95e7dae2137d68fc2d417816c004770fb_265678.fix
@@ -2723,6 +2737,7 @@ dump/test-vectors/txn/fixtures/programs/e76f3482279ffdb1c9010a7d13e57c7ba50f5747
 dump/test-vectors/txn/fixtures/programs/e781dc0a152bc21adf690ed725f7a96bfcdf70a2_265678.fix
 dump/test-vectors/txn/fixtures/programs/e7bbc6fed88971fd6dfd140921e1226b0597dc25_265678.fix
 dump/test-vectors/txn/fixtures/programs/e7db4bd1e2a93d6b77ef06bb6f952ec39a591720_265678.fix
+dump/test-vectors/txn/fixtures/programs/e7ea7ace535e604a8e6ee07cf791292490bd29e3_3882152.fix
 dump/test-vectors/txn/fixtures/programs/e7fcaf588511d4df2cb28332a5e921865c38e867_265678.fix
 dump/test-vectors/txn/fixtures/programs/e81b280c49a92d7a13f1ea782650b381b74125f6_265678.fix
 dump/test-vectors/txn/fixtures/programs/e826f6cc73811d8d819524a59642373c0f03a9f1_265678.fix
@@ -3022,8 +3037,4 @@ dump/test-vectors/txn/fixtures/programs/txn-3eDdfZE6HswPxFKrtnQPsEmTkyL1iP57gRPE
 dump/test-vectors/txn/fixtures/programs/txn-3VZwmGFE78PAGbUV9SuPE4EgqAkB7kQLDuoE4iFNberYV3n4yPm37eedu8gmm7HRiogLUPRrZYRHqQSz6DZtbiKq.fix
 dump/test-vectors/txn/fixtures/programs/txn-5V5uB8Ro1rVPmRJPH5Yhfxr5sPAXEFWGsA4d2YbBDaTEaJn6Key9VuCEvuRaZCi6ziBfAtRUH1shuma9SNqsHSKP.fix
 dump/test-vectors/txn/fixtures/programs/txn-CA7V2nP2oagjGvqaqRRm7kyRpk2Q58gA3vFHQs7NvYv4Y6bNtoNX1xp5fuQPPL2ZNStqszAuGmDYfEG64BQhpKd.fix
-dump/test-vectors/txn/fixtures/programs/1fff2d993f4d7677640b2b3397320496b076e854_3506222.fix
-dump/test-vectors/txn/fixtures/programs/21fb4857674201e9f6c173c1f2e83556718c401e_1556049.fix
-dump/test-vectors/txn/fixtures/programs/338a0b377eb143b9d2520fd81d6b8658ea71d32a_1183730.fix
-dump/test-vectors/txn/fixtures/programs/45dd4971a31ae58798211458d14551780be22c7a_1633256.fix
-dump/test-vectors/txn/fixtures/programs/805e0cd05df6ceb015a08086e9bcfab51f559747_180823.fix
+dump/test-vectors/txn/fixtures/programs/txn-Sz5UjeMULjCMyvctj8537vMdk3q44To3BjeFpi5PBFZowQWJMmZXQw6VUEJBDCMaE9m4yEnVQCMhqYgp1T5vQea.fix
```

### src/flamenco/features/feature_map.json
```diff
@@ -146,7 +146,7 @@
   {"name":"prevent_rent_paying_rent_recipients","pubkey": "Fab5oP3DmsLYCiQZXdjyqT3ukFFPrsmqhXU4WU1AWVVF","cleaned_up":[1,18,0],"activated_on_all_clusters":1},
   {"name":"delay_visibility_of_program_deployment","pubkey": "GmuBvtFb2aHfSfMXpuFeWZGHyDeCLPS79s48fmCWCfM5","cleaned_up":[1,18,0],"activated_on_all_clusters":1},
   {"name":"apply_cost_tracker_during_replay","pubkey": "2ry7ygxiYURULZCrypHhveanvP5tzZ4toRwVp89oCNSj"},
-  {"name":"deplete_cu_meter_on_vm_failure","pubkey": "B7H2caeia4ZFcpE3QcgMqbiWiBtWrdBRBSJ1DY6Ktxbq"},
+  {"name":"deplete_cu_meter_on_vm_failure","pubkey": "B7H2caeia4ZFcpE3QcgMqbiWiBtWrdBRBSJ1DY6Ktxbq","comment":"do not set activated_on_all_clusters for this - it significantly degrades vm fuzzing discovery"},
   {"name":"bpf_account_data_direct_mapping","pubkey": "AjX3A4Nv2rzUuATEUWLP4rrBaBropyUnHxEvFDj1dKbx","old": "GJVDwRkUPNdk9QaK4VsU4g1N41QNxhy1hevjf8kz45Mq"},
   {"name":"add_set_tx_loaded_accounts_data_size_instruction","pubkey": "G6vbf1UBok8MWb8m25ex86aoQHeKTzDKzuZADHkShqm6","cleaned_up":[1,18,0],"activated_on_all_clusters":1},
   {"name":"switch_to_new_elf_parser","pubkey": "Cdkc8PPTeTNUPoZEfCY5AyetUrEdkZtNPMgz58nqyaHD","cleaned_up":[2,1,0],"activated_on_all_clusters":1},
```

### src/flamenco/runtime/context/fd_exec_txn_ctx.c
```diff
@@ -234,8 +234,9 @@ fd_exec_txn_ctx_setup_basic( fd_exec_txn_ctx_t * txn_ctx ) {
   txn_ctx->instr_err_idx   = INT_MAX;
   txn_ctx->capture_ctx     = NULL;
 
-  txn_ctx->instr_info_cnt     = 0;
-  txn_ctx->instr_trace_length = 0;
+  txn_ctx->instr_info_cnt     = 0UL;
+  txn_ctx->cpi_instr_info_cnt = 0UL;
+  txn_ctx->instr_trace_length = 0UL;
 
   txn_ctx->exec_err      = 0;
   txn_ctx->exec_err_kind = FD_EXECUTOR_ERR_KIND_NONE;
```

### src/flamenco/runtime/context/fd_exec_txn_ctx.h
```diff
@@ -144,6 +144,15 @@ struct __attribute__((aligned(8UL))) fd_exec_txn_ctx {
   fd_instr_info_t             instr_infos[FD_MAX_INSTRUCTION_TRACE_LENGTH];
   ulong                       instr_info_cnt;
 
+  /* These instr infos are statically allocated at the beginning of a transaction
+     and are only written to / referred to within the VM. It's kept
+     at the transaction level because syscalls like `GetProcessedSiblingInstruction()`
+     may refer to instructions processed earlier in the transaction. */
+  fd_instr_info_t             cpi_instr_infos[FD_MAX_INSTRUCTION_TRACE_LENGTH];
+  ulong                       cpi_instr_info_cnt;
+
+  /* Each instr info within `instr_trace` may refer to an `instr_infos` or `cpi_instr_infos`
+     entry. */
   fd_exec_instr_trace_entry_t instr_trace[FD_MAX_INSTRUCTION_TRACE_LENGTH]; /* Instruction trace */
   ulong                       instr_trace_length;                           /* Number of instructions in the trace */
 
```

### src/flamenco/runtime/tests/fd_dump_pb.c
```diff
@@ -408,7 +408,6 @@ create_block_context_protobuf_from_block( fd_exec_test_block_context_t * block_c
     fd_solana_secp256r1_program_id,
     fd_solana_zk_elgamal_proof_program_id,
     fd_solana_ed25519_sig_verify_program_id,
-    fd_solana_spl_native_mint_id,
   };
   ulong num_sysvar_entries    = (sizeof(fd_relevant_sysvar_ids) / sizeof(fd_pubkey_t));
   ulong num_loaded_builtins   = (sizeof(loaded_builtins) / sizeof(fd_pubkey_t));
@@ -702,7 +701,6 @@ create_txn_context_protobuf_from_txn( fd_exec_test_txn_context_t * txn_context_m
     fd_solana_secp256r1_program_id,
     fd_solana_zk_elgamal_proof_program_id,
     fd_solana_ed25519_sig_verify_program_id,
-    fd_solana_spl_native_mint_id,
   };
   const ulong num_loaded_builtins = (sizeof(loaded_builtins) / sizeof(fd_pubkey_t));
 
```

### src/flamenco/runtime/tests/run_ledger_tests_all.txt
```diff
@@ -73,3 +73,4 @@ src/flamenco/runtime/tests/run_ledger_test.sh -l mainnet-325467935-no-rent -s sn
 src/flamenco/runtime/tests/run_ledger_test.sh -l testnet-283927487-no-rent -s snapshot-283927486-7gCbg5g4BnD9SkQUjpHvhepWsQTpo2WaZaA5bhcNBMhG.tar.zst -p 60 -y 16 -m 5000000 -e 283927497 -c 2.0.23
 src/flamenco/runtime/tests/run_ledger_test.sh -l testnet-321168308 -s snapshot-321168307-DecxjCHDsiQgbqZPHptgz1tystKi3QmV3Rd3QEgcxs2W.tar.zst -p 60 -y 16 -m 5000000 -e 321168308 -c 2.1.13
 src/flamenco/runtime/tests/run_ledger_test.sh -l v208-zk-sdk-ledger-no-rent -s snapshot-1-GNxLdkaRgGzZSKj79d7yUXK8Nd7dv87WckoCdzQYH4X2.tar.zst -p 60 -y 16 -m 500000 -e 82 -c 2.1.14
+src/flamenco/runtime/tests/run_ledger_test.sh -l mainnet-327324660 -s snapshot-327324659-85G1Hp5JsY1EiixLgFk1VRacP9bu1EGczBunvuJWgMDw.tar.zst -p 60 -y 16 -m 2000000 -e 327324660 -c 2.1.14
```

### src/flamenco/vm/syscall/fd_vm_syscall_cpi_common.c
```diff
@@ -861,7 +861,7 @@ VM_SYSCALL_CPI_ENTRYPOINT( void *  _vm,
 
   /* Create the instruction to execute (in the input format the FD runtime expects) from
      the translated CPI ABI inputs. */
-  fd_instr_info_t instruction_to_execute[ 1 ];
+  fd_instr_info_t * instruction_to_execute = &vm->instr_ctx->txn_ctx->cpi_instr_infos[ vm->instr_ctx->txn_ctx->cpi_instr_info_cnt++ ];
 
   err = VM_SYSCALL_CPI_INSTRUCTION_TO_INSTR_FUNC( vm, cpi_instruction, cpi_account_metas, program_id, data, instruction_to_execute );
   if( FD_UNLIKELY( err ) ) {
```
