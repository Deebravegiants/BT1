# [?] fix(core/eckhart): fix slip39 overflow bug

## Summary
Severity: Unknown
Chain: Trezor
Component: trezor/trezor-firmware
Published: 2025-07-08
Source: https://github.com/trezor/trezor-firmware/commit/34921907b0d560e5eba1321e7798acf1bb3ed0c7
Type: security-commit

## Details
fix(core/eckhart): fix slip39 overflow bug

[no changelog]

## Patch
### core/embed/rust/src/ui/layout_eckhart/firmware/keyboard/slip39.rs
```diff
@@ -142,13 +142,18 @@ impl Component for Slip39Input {
             let input_len = self.textbox.content().len();
 
             // Get last pending character, if any.
-            let last = if let (Some(key), Some(press)) =
-                (self.multi_tap.pending_key(), self.multi_tap.pending_press())
-            {
-                Some(&Self::keys()[key][press..(press + 1)])
-            } else {
-                None
-            };
+            let last = self
+                .multi_tap
+                .pending_key()
+                .zip(self.multi_tap.pending_press())
+                .and_then(|(key, press)| {
+                    Self::keys().get(key).map(|group| {
+                        debug_assert!(!group.is_empty());
+                        // Wrap around if press count exceeds group length
+                        let press = press % group.len();
+                        &group[press..press + 1]
+                    })
+                });
 
             // Initial position for drawing the icons
             let mut cursor = area.center().ofs(Offset::x(-self.size() / 2));
```

### tests/click_tests/test_recovery.py
```diff
@@ -14,6 +14,7 @@
 # You should have received a copy of the License along with this library.
 # If not, see <https://www.gnu.org/licenses/lgpl-3.0.html>.
 
+import time
 from contextlib import contextmanager
 from typing import TYPE_CHECKING, Generator
 
@@ -23,6 +24,8 @@
 
 from ..common import MNEMONIC12, LayoutType, MNEMONIC_SLIP39_BASIC_20_3of6
 from . import recovery
+from .common import go_next
+from .test_autolock import PIN4, set_autolock_delay, unlock_dry_run
 
 if TYPE_CHECKING:
     from trezorlib.debuglink import DebugLink
@@ -152,3 +155,54 @@ def test_recovery_cancel_issue4613(device_handler: "BackgroundDeviceHandler"):
     assert layout.main_component() == "Homescreen"
     features = device_handler.client.refresh_features()
     assert features.recovery_status == messages.RecoveryStatus.Nothing
+
+
+@pytest.mark.models(skip=["legacy", "safe3"])
+@pytest.mark.setup_client(pin=PIN4)
+def test_recovery_slip39_issue5306(device_handler: "BackgroundDeviceHandler"):
+    """Test for issue fixed in PR #5306: After tapping the key more times
+    than its length, there was an internal error UF."""
+
+    set_autolock_delay(device_handler, 10_000)
+    debug = device_handler.debuglink()
+
+    device_handler.run(device.recover, type=messages.RecoveryType.DryRun)
+
+    unlock_dry_run(debug)
+
+    # select 20 words
+    recovery.select_number_of_words(debug, 20)
+
+    # go to mnemonic keyboard
+    if debug.layout_type in (LayoutType.Bolt, LayoutType.Delizia, LayoutType.Eckhart):
+        layout = go_next(debug)
+        assert layout.main_component() == "MnemonicKeyboard"
+    elif debug.layout_type is LayoutType.Caesar:
+        debug.press_right()
+        layout = debug.read_layout()
+        assert "MnemonicKeyboard" in layout.all_components()
+    else:
+        raise ValueError(f"Unsupported layout type: {debug.layout_type}")
+
+    # click the first key multiple times (more times than its length) to trigger the issue
+    coords = list(debug.button_actions.type_word("a", is_slip39=True))
+    for _ in range(3):
+        debug.click(coords[0])
+
+    # Make sure, the keyboard did not crash
+    layout = debug.read_layout()
+    if debug.layout_type in (LayoutType.Bolt, LayoutType.Delizia, LayoutType.Eckhart):
+        assert layout.main_component() == "MnemonicKeyboard"
+    elif debug.layout_type is LayoutType.Caesar:
+        assert "MnemonicKeyboard" in layout.all_components()
+    else:
+        raise ValueError(f"Unsupported layout type: {debug.layout_type}")
+
+    # wait for the keyboard to lock
+    time.sleep(10.1)
+    if debug.layout_type is LayoutType.Eckhart:
+        assert debug.read_layout().main_component() == "Homescreen"
+    else:
+        assert debug.read_layout().main_component() == "Lockscreen"
+    with pytest.raises(exceptions.Cancelled):
+        device_handler.result()
```

### tests/ui_tests/fixtures.json
```diff
@@ -816,6 +816,7 @@
 "T2T1_cs_test_recovery.py::test_recovery_cancel_issue4613": "6a89fa27ea318f1033a48d9686df13d4a110a2bd9a4f35c367cf35616c320762",
 "T2T1_cs_test_recovery.py::test_recovery_cancel_number_of_words": "01da07f9b71bdd700ad3b0b9e4480c9e8567ba57383d406d380cef6d50d3b197",
 "T2T1_cs_test_recovery.py::test_recovery_slip39_basic": "17b72f08784965af83954d7eeee74e364d27796ef8f40d4ae609ef66ccedf6d3",
+"T2T1_cs_test_recovery.py::test_recovery_slip39_issue5306": "fec0cd91717f0b7e2240cc57505388a432cdd7f58d17b95e2a651a4baa9aaf01",
 "T2T1_cs_test_repeated_backup.py::test_repeated_backup_via_device": "5817c97527e0da63626d3e8f6f6bfe55344d149f89ae9addd6f3915e83bc1ea1",
 "T2T1_cs_test_reset_bip39.py::test_reset_bip39": "a2f8c63628d41aff913ef3ccba61f8262bb90b535578ce349cadbb63294bf8cf",
 "T2T1_cs_test_reset_slip39_advanced.py::test_reset_slip39_advanced[16of16]": "f7683e45a6e304dd3e76501d96f4da45aacc7186a2820149eeb9d61dedd58b96",
@@ -868,6 +869,7 @@
 "T2T1_de_test_recovery.py::test_recovery_cancel_issue4613": "1d4497515e07d3674ee32d909fdbe8f4097aa8e28f040202f753a33a65f97340",
 "T2T1_de_test_recovery.py::test_recovery_cancel_number_of_words": "745e1d65da0afade34db98a1715ffd5cd64789025d48f30df1da4e271ce7e8dc",
 "T2T1_de_test_recovery.py::test_recovery_slip39_basic": "867f0c4e66e867d9e32d19df864d4e2bb4733d6d5a09b882cc1d4951d427ab6d",
+"T2T1_de_test_recovery.py::test_recovery_slip39_issue5306": "5a6d2b1cc819a0353bc249459032ad9bab96436b831ab23e251784a3dacc35a1",
 "T2T1_de_test_repeated_backup.py::test_repeated_backup_via_device": "c1c365652aae042f06c8ff829ad9176f1ad5285ab722606c6de502edad42538b",
 "T2T1_de_test_reset_bip39.py::test_reset_bip39": "6d176c432d3d835fdf3fe8f437751f3c58a41be553071008a9cad68efb26874c",
 "T2T1_de_test_reset_slip39_advanced.py::test_reset_slip39_advanced[16of16]": "2ea57b5b040accc10a632bacbdd46434a0e5acdd1c240a0078f6cf8c7d6c66f8",
@@ -920,6 +922,7 @@
 "T2T1_en_test_recovery.py::test_recovery_cancel_issue4613": "fe766874bc3b50bcb5dd735b8d02eaf55ae18f6a9d7938d44f20cc6c5c2d1475",
 "T2T1_en_test_recovery.py::test_recovery_cancel_number_of_words": "7d489d3b0c63d802139b83c1ad2607793b1232150d115c2f15c597d782a02e45",
 "T2T1_en_test_recovery.py::test_recovery_slip39_basic": "0bbdd3d4c70a946175718c052fdcb4513f3aa4018d8390ef47ddea991ce0d704",
+"T2T1_en_test_recovery.py::test_recovery_slip39_issue5306": "7bdf1acd9640e56e689bcaf50a13eb9bd42a9f4f1bcd4e08c4bf280b1ce22e31",
 "T2T1_en_test_repeated_backup.py::test_repeated_backup_via_device": "41e1a6095a0cbbe969ab468f0aaa3d67d3ee7b9eb6bad2fd89c6f615ad038b76",
 "T2T1_en_test_reset_bip39.py::test_reset_bip39": "5af195b13687cc0c4d6fcf481eedbdb06e48a074f62aa86fd28cc9f9f1a60752",
 "T2T1_en_test_reset_slip39_advanced.py::test_reset_slip39_advanced[16of16]": "563bfddbdbc705be3f556c4be347af2c776a99b351ca95029b646e662f712d64",
@@ -972,6 +975,7 @@
 "T2T1_es_test_recovery.py::test_recovery_cancel_issue4613": "f7a6e6b6908aa3b864775eb0f18b61708b0bcd49ad3e74ffbabefae4ab12cc8c",
 "T2T1_es_test_recovery.py::test_recovery_cancel_number_of_words": "df31777c1cf1bcf792a93f1127bfc88f46535d5fc95c8e62cf7a615094d7d36d",
 "T2T1_es_test_recovery.py::test_recovery_slip39_basic": "410ad35e9970b35b55c48c4b6c225ad3e63342a83f62e3161cfbd31893069579",
+"T2T1_es_test_recovery.py::test_recovery_slip39_issue5306": "ec23602132516a33543116ef0f01cea9218a7755a167228ee7924590b104b076",
 "T2T1_es_test_repeated_backup.py::test_repeated_backup_via_device": "53d0f5c04da015b3979ddd2481adacad964ba1ad32c21bd45f28f381267c906c",
 "T2T1_es_test_reset_bip39.py::test_reset_bip39": "e5286038a631c727dad181308d78f7d2218ea465bcc17174e455eadb7ceea920",
 "T2T1_es_test_reset_slip39_advanced.py::test_reset_slip39_advanced[16of16]": "af2ff498d75af426ad6030bae7ba07990bb83e3f05542be1c318d792b7673067",
@@ -1024,6 +1028,7 @@
 "T2T1_fr_test_recovery.py::test_recovery_cancel_issue4613": "dce932978ee36e18b4db8da145ce7af9bbd1d63112ce06b3466792c5b0ef7792",
 "T2T1_fr_test_recovery.py::test_recovery_cancel_number_of_words": "2de15ea31367bd623c7c3eb52e527f8177b05cf2937a37d74e050605c6be8b6f",
 "T2T1_fr_test_recovery.py::test_recovery_slip39_basic": "0f399f6553d78a863e8252a3e292098ab337d6acb26f59fbcd36cc27379fa726",
+"T2T1_fr_test_recovery.py::test_recovery_slip39_issue5306": "393f542d276c52ef2906816cbfc3dd1962e84108f7ac5dcc26c0ed11d595d7e3",
 "T2T1_fr_test_repeated_backup.py::test_repeated_backup_via_device": "b3099634a0106bdf08ec3ca6f38093812273aaf7532ad17f47656cf1f374e844",
 "T2T1_fr_test_reset_bip39.py::test_reset_bip39": "e4a677eb3ea4b16d968d12402af03fbfa50a7ab648c6b6e3a7bf4c45d3da698e",
 "T2T1_fr_test_reset_slip39_advanced.py::test_reset_slip39_advanced[16of16]": "8c367669cc7128f346e4c765f6ae3ff122d34cfafc9027f1171ac15ec6ef65b3",
@@ -1076,6 +1081,7 @@
 "T2T1_pt_test_recovery.py::test_recovery_cancel_issue4613": "69b4e8f4aacb57e63ef0d96a5dfb691271b4d324b7852dbf9038ac458f7a7ddd",
 "T2T1_pt_test_recovery.py::test_recovery_cancel_number_of_words": "8ae102c86719d886a628c4b1225fde09f5fd143421842ee34bdffb8d532e37e4",
 "T2T1_pt_test_recovery.py::test_recovery_slip39_basic": "1a879653b955c074f79c2d5e083b752159f1275f5723ff5f041496abe1b3fd62",
+"T2T1_pt_test_recovery.py::test_recovery_slip39_issue5306": "2fee2d3ddbf20a5be5b5803a7ff4c29cf83a43d310b9cdbb6ea61ff350109f62",
 "T2T1_pt_test_repeated_backup.py::test_repeated_backup_via_device": "c4112ba439707d1f1aabad7fefba38c7c37b1110df8973cbda7e2c594038124b",
 "T2T1_pt_test_reset_bip39.py::test_reset_bip39": "35083231c0e27a59af123af273b83c65b411b669f1a023cf98eb0b2b9036176b",
 "T2T1_pt_test_reset_slip39_advanced.py::test_reset_slip39_advanced[16of16]": "5f4c46af3021797e522b99a75918765ef6694630892aa6dc33fe661779e9fc77",
@@ -18916,6 +18922,7 @@
 "T3T1_cs_test_recovery.py::test_recovery_cancel_issue4613": "89bec24d34b63a486b6ef3ed3d6ccbffaaf858ab8f21d39e2b7b4b4e14944863",
 "T3T1_cs_test_recovery.py::test_recovery_cancel_number_of_words": "5f43b7ef903f251cc61a0fda3424be3acc7eb6113b9242dcea0056543abf0e0e",
 "T3T1_cs_test_recovery.py::test_recovery_slip39_basic": "0711778f13861849188a284aca0f1315e29f68bd89d4a3ae87ab3a2519d3e4eb",
+"T3T1_cs_test_recovery.py::test_recovery_slip39_issue5306": "05233ebce81b625be904f9477b196e9418d9814e3ec71d169a1087d775502be5",
 "T3T1_cs_test_repeated_backup.py::test_repeated_backup_via_device": "d235cd338d4ae28598a00df255aab0266babbdd11fcc0982209e2938b7a3ecf1",
 "T3T1_cs_test_reset_bip39.py::test_reset_bip39": "6bff7a7eed8fd54293e0c5c726c3c8841a49608d7d9fddb2acc863d515948809",
 "T3T1_cs_test_reset_slip39_advanced.py::test_reset_slip39_advanced[16of16]": "b15cd79b82c3b874fad637a5ef4d142edfaf387d27f7ab4937ed578e48077b41",
@@ -18973,6 +18980,7 @@
 "T3T1_de_test_recovery.py::test_recovery_cancel_issue4613": "6d31bd43b2bd2a8c9e25ef9f48a066c852669e5e46bc4a463786d67b5e91b7a8",
 "T3T1_de_test_recovery.py::test_recovery_cancel_number_of_words": "247160c18c462b92b558263f49d4f79974ea95202ab3faa0ef33f50a2d21d2f7",
 "T3T1_de_test_recovery.py::test_recovery_slip39_basic": "314caaeb33d6bfc7e9c4f7977b486516eb338ea2220ff13ee40f62beb0179303",
+"T3T1_de_test_recovery.py::test_recovery_slip39_issue5306": "7bbd2a980215b1fd61d76c0e5930dd9917471952b81eab1153b99f874ba69ccb",
 "T3T1_de_test_repeated_backup.py::test_repeated_backup_via_device": "203b2efbd1df12209a06f2124af5cfbdbaaaf02cb17a11d9bd4309a25b8b9894",
 "T3T1_de_test_reset_bip39.py::test_reset_bip39": "b9248b8bfd35de9b4e268db9638dbf1e1710e5ae25115c88c408d1e4260970ad",
 "T3T1_de_test_reset_slip39_advanced.py::test_reset_slip39_advanced[16of16]": "4f925c8ff2782f56731f2faa831b66970b5af3d0faf2efe82d7f144ca49e56a1",
@@ -19030,6 +19038,7 @@
 "T3T1_en_test_recovery.py::test_recovery_cancel_issue4613": "0413fa152a7ae8d1e30659375165d2356faccd832e4fd01ac75fc62eba0b1c16",
 "T3T1_en_test_recovery.py::test_recovery_cancel_number_of_words": "40c22731deba58bc21a75bd77f5fba9fee11d84cce1c57d1402a941a79650189",
 "T3T1_en_test_recovery.py::test_recovery_slip39_basic": "6989ce3c9a9ef7484fe41a75d9a9023e110a535f4c8be2c72406c40f71f484cd",
+"T3T1_en_test_recovery.py::test_recovery_slip39_issue5306": "dc3cf81707370b57510c6ad98eb3b9a80b2b55bbb0fa8e5ca0ebd58ebea53982",
 "T3T1_en_test_repeated_backup.py::test_repeated_backup_via_device": "f2d30ed07d3d3013b690ec8d90eedd58a63d58eb497dec6aa97490331ba120bc",
 "T3T1_en_test_reset_bip39.py::test_reset_bip39": "bfd6ba797bd3277fb45ba705f2e8ca12a869087c1a4592a0b11587486545af14",
 "T3T1_en_test_reset_slip39_advanced.py::test_reset_slip39_advanced[16of16]": "e6fff7f7a396a62a202550800b7387ba58757166f82f889a93deb12ee9ebf061",
@@ -19087,6 +19096,7 @@
 "T3T1_es_test_recovery.py::test_recovery_cancel_issue4613": "3bbe4f0e3d53b266a8a3895611a8b4079e3562c8e7a5b97ac19e3e42d9b98a5a",
 "T3T1_es_test_recovery.py::test_recovery_cancel_number_of_words": "819f4d4a518fd03805dcfaf583258e2788da00a2a54931981af2464f72971e65",
 "T3T1_es_test_recovery.py::test_recovery_slip39_basic": "75267dc5782cd86264a65ad502e1ddf413f8e278fe2f073c10613bd40e784849",
+"T3T1_es_test_recovery.py::test_recovery_slip39_issue5306": "dac0c21b41e7cd8c16aad001e76e17ba401c794caca46578133cf99a91618698",
 "T3T1_es_test_repeated_backup.py::test_repeated_backup_via_device": "8eb2ce71cc875829b44ea3bc68d8e75a3de66b95fb6769414a14ce1e47322905",
 "T3T1_es_test_reset_bip39.py::test_reset_bip39": "775b7800d0acde5083dc8e0e4084fa70dfb8c74174d985af78bdb33e975e9096",
 "T3T1_es_test_reset_slip39_advanced.py::test_reset_slip39_advanced[16of16]": "142e89d0af9c3a185adf6b4a3a8c2b9b29ad4a5ab8d2588ffcdc90b772cf322b",
@@ -19144,6 +19154,7 @@
 "T3T1_fr_test_recovery.py::test_recovery_cancel_issue4613": "63ce53c67f6abb16b4545c35f88f89f24c59ca0f865b321a877e39281d60652e",
 "T3T1_fr_test_recovery.py::test_recovery_cancel_number_of_words": "195b4d7ea094959d5b61dde6bb9d4e31165885f54099ae10ed99ab5e8d2fe14e",
 "T3T1_fr_test_recovery.py::test_recovery_slip39_basic": "ec1991f833adfdf98cdcf09a3bd828f44ab39600765bec8459d2873d9da73b77",
+"T3T1_fr_test_recovery.py::test_recovery_slip39_issue5306": "d2a19f6035187cde8e65727bf3d66bd12a9ce3b7eedb79ae53d899a0eba8fb43",
 "T3T1_fr_test_repeated_backup.py::test_repeated_backup_via_device": "b5819a83a7ed426a77097cfa5cbece16e848f646946ac4b4607b55f62390bd7a",
 "T3T1_fr_test_reset_bip39.py::test_reset_bip39": "229b2d3bab421f688806dca5fc095b9a15331c2adba4fbe5510e20af6b4852e4",
 "T3T1_fr_test_reset_slip39_advanced.py::test_reset_slip39_advanced[16of16]": "ef181f48b10b5138411a9f9b9d7be82e5f7bf53d48a5bbeb607bf108ef942659",
@@ -19201,6 +19212,7 @@
 "T3T1_pt_test_recovery.py::test_recovery_cancel_issue4613": "6ca26a02a3c05d90b3aae3c8f49b2171f46b97182ec8962537ae5690662b86c3",
 "T3T1_pt_test_recovery.py::test_recovery_cancel_number_of_words": "62e74061f5f7450330de79565a5e6e6eb0ba2bdeac812b9f5f02d22b295c3570",
 "T3T1_pt_test_recovery.py::test_recovery_slip39_basic": "b9c123296ce9d6b167eef45d31a420a97cba8eacc8f891cbb3af163e595b27be",
+"T3T1_pt_test_recovery.py::test_recovery_slip39_issue5306": "0d4bf36abb59639570a6a137ba2e8a8374923a3aad8a5659a96faa671bfbe19e",
 "T3T1_pt_test_repeated_backup.py::test_repeated_backup_via_device": "67d99be3e9fb33b72f8b27f3ec16068c1f5f60c5b35722750e53e25ffb5accbb",
 "T3T1_pt_test_reset_bip39.py::test_reset_bip39": "c5cdc6ba952e8c83208c8aa5e0ea849bb133f3b75c62b3f6caf7b424887b5933",
 "T3T1_pt_test_reset_slip39_advanced.py::test_reset_slip39_advanced[16of16]": "3508b77247d53dea952557c9046b464875d070c8268402b361c662f5e2a160d0",
@@ -27908,6 +27920,7 @@
 "T3W1_cs_test_recovery.py::test_recovery_cancel_issue4613": "de520deafc496a64b337ef4528c9fb738f7c5a315f28da2efe43abd3678d0789",
 "T3W1_cs_test_recovery.py::test_recovery_cancel_number_of_words": "12b24abffdda6e5d90c53ed08c669817f722ca023c3eae757e768f1d1078f699",
 "T3W1_cs_test_recovery.py::test_recovery_slip39_basic": "5ae0d438d686f37c6fd51b3c25e736d0fd7ab082cd4fc55e8456d59b3fbdc964",
+"T3W1_cs_test_recovery.py::test_recovery_slip39_issue5306": "2906f99e044a438ac0c1cf8ca663df603f3dd46118fd6da4d3a784d320fa3a1f",
 "T3W1_cs_test_repeated_backup.py::test_repeated_backup_via_device": "1166907aa481bdf9cca13201e6f04c6d815d9af425cd2f9a6a9aa1ec50ecd3e8",
 "T3W1_cs_test_reset_bip39.py::test_reset_bip39": "73e91366636790095a0292cd9102fa336da016551cfdd4b57fd849d6c5c36388",
 "T3W1_cs_test_reset_slip39_advanced.py::test_reset_slip39_advanced[16of16]": "fbfe5886ecf7c699180b3a7edbf54fd5f97867115f8ba3e93f63beeb40db22ba",
@@ -27960,6 +27973,7 @@
 "T3W1_de_test_recovery.py::test_recovery_cancel_issue4613": "7d8991e7308ee021e46bddda9d07a9775bbfa814b611fedc5cf7dae6827aa2b5",
 "T3W1_de_test_recovery.py::test_recovery_cancel_number_of_words": "2c01135966cd038e97e1e5245c2f42f60cc9d63a6e2e6aced498114840f5d68f",
 "T3W1_de_test_recovery.py::test_recovery_slip39_basic": "6072fa1f86a9b22fc2ed57aeb78919834fa94dcb1b14efad722c6ab0d6639598",
+"T3W1_de_test_recovery.py::test_recovery_slip39_issue5306": "e50a097127ad923ea172a6a9513fa93dc84d0b1210a81756d4c676259f5b4e48",
 "T3W1_de_test_repeated_backup.py::test_repeated_backup_via_device": "17f33222e3ca4cc66db3964991a05484e812e31785df126ef83c2a65a31f8178",
 "T3W1_de_test_reset_bip39.py::test_reset_bip39": "6287763bffbe53fec934a4cf6661506cbd0be945fe05fc85075b7eeac3444079",
 "T3W1_de_test_reset_slip39_advanced.py::test_reset_slip39_advanced[16of16]": "ab654ada408857a84f48dd060a6b51690375bb1ee641d08e442a7ad051498f97",
@@ -28012,6 +28026,7 @@
 "T3W1_en_test_recovery.py::test_recovery_cancel_issue4613": "9d818408ccdea699d4e4e6aff85789d1773c12b21b6698500505011675818001",
 "T3W1_en_test_recovery.py::test_recovery_cancel_number_of_words": "4662fe078d62c7ac2cc64db954fd21a75a640a9cada784740c38263af4008fcb",
 "T3W1_en_test_recovery.py::test_recovery_slip39_basic": "141fc0637e9a0059040083b87e8bd65659916c942c80fc7e1046283a92effc50",
+"T3W1_en_test_recovery.py::test_recovery_slip39_issue5306": "fe98bce4306f5d2f1f89643c7ab72322880e3cdd52b661ca14dbc59e7f08a7fa",
 "T3W1_en_test_repeated_backup.py::test_repeated_backup_via_device": "172a40dba9b9f542efb045c9e0093c1b65ed3aba2c775fd839514c12bea1fecb",
 "T3W1_en_test_reset_bip39.py::test_reset_bip39": "df219c8625abf836972d203c36a4211b6c72e0b7cc22bd37c34ce2ca4b06101d",
 "T3W1_en_test_reset_slip39_advanced.py::test_reset_slip39_advanced[16of16]": "c790af906b6b5ca6110a0e17ca8dc210721d16c829585c0a80e4bb59fe05b55e",
@@ -28064,6 +28079,7 @@
 "T3W1_es_test_recovery.py::test_recovery_cancel_issue4613": "897aa0a83b066deff7b19af055189d95d7158d35206df969b8f630b3f8da7718",
 "T3W1_es_test_recovery.py::test_recovery_cancel_number_of_words": "ce77225e26a54f3bb766bfcdb3f6441d365a911eb3db64dd8bc89fcf8a949683",
 "T3W1_es_test_recovery.py::test_recovery_slip39_basic": "ebdb9a4b378a5f3c96ea071125d75f5d026433d8993f5c3ee203061310d13f1f",
+"T3W1_es_test_recovery.py::test_recovery_slip39_issue5306": "94ba6d5fe4fa75318781406343eccc258c24239c608b703ff868b37e2083339f",
 "T3W1_es_test_repeated_backup.py::test_repeated_backup_via_device": "c31f8fa0ca38780b6bbb1f5e0221ab75229d1b912b7fdf9592bd4e4e88e67801",
 "T3W1_es_test_reset_bip39.py::test_reset_bip39": "cd9275c926c5364825f52b1825bcc372600f275d180023311c9b9e46d283ffe3",
 "T3W1_es_test_reset_slip39_advanced.py::test_reset_slip39_advanced[16of16]": "c53ab8bdbeb71afa22edb6179d3cfeb5649c9ae1edd430fdfaa4b3ebbd8980a8",
@@ -28116,6 +28132,7 @@
 "T3W1_fr_test_recovery.py::test_recovery_cancel_issue4613": "8716ea03c7df9c4fa4cbecb81fc0a9e6067bd7535254070d6f36a1e67d6edcbf",
 "T3W1_fr_test_recovery.py::test_recovery_cancel_number_of_words": "0714aa6589b4285982c7e68255fa685afacd4508e9dfc8877075a639cd07ed62",
 "T3W1_fr_test_recovery.py::test_recovery_slip39_basic": "a94a7112ff84456d38fedf9fdda64b7ea3052f870a930bd4f7dac84626679a63",
+"T3W1_fr_test_recovery.py::test_recovery_slip39_issue5306": "02eca2deb6a6835edabf8cb775f93fa158e090120df2871f4fe34e358d9f0783",
 "T3W1_fr_test_repeated_backup.py::test_repeated_backup_via_device": "90e7787c10fffcbfbe3228c87dfa58b6dc0d715ab669479d0dc14bfc9628f641",
 "T3W1_fr_test_reset_bip39.py::test_reset_bip39": "7cf66129856ae52a22379dfbe09625e08cb195e1261b7af0c87480fe3b001a7a",
 "T3W1_fr_test_reset_slip39_advanced.py::test_reset_slip39_advanced[16of16]": "1c117dcd982bc1aa1bcbb4475b665c27e77eb9038ecc43128d65ebe204c8bc25",
@@ -28168,6 +28185,7 @@
 "T3W1_pt_test_recovery.py::test_recovery_cancel_issue4613": "829a19863e3ab98a4199682ccb7d5d582a8e02243ee7c79b593e8778882694f5",
 "T3W1_pt_test_recovery.py::test_recovery_cancel_number_of_words": "79857abb33f8eac95e6c08359841b7658244d3e18efb2bfac0f5f0846e44819c",
 "T3W1_pt_test_recovery.py::test_recovery_slip39_basic": "ce14d08aff2b63cb889ddea826a0886ba049da8a61c4ff751dbbc379c952f5f6",
+"T3W1_pt_test_recovery.py::test_recovery_slip39_issue5306": "7edb0803e6b1d73523027d9d8644eec2e3fe1f4f33f44bb91bf621d65b090c72",
 "T3W1_pt_test_repeated_backup.py::test_repeated_backup_via_device": "8bf465ea1647ff28d9082e12e6ebd4a8f18bca88ea52a94807d647c50536b0bd",
 "T3W1_pt_test_reset_bip39.py::test_reset_bip39": "5c9fb8bb89cf2e889236e5ccc88c468c96598a623664fb09182ac3e3a12376c7",
 "T3W1_pt_test_reset_slip39_advanced.py::test_reset_slip39_advanced[16of16]": "8a0033839506dc9971064fbe2bfeb0bfa7bf012a5441ff793bcf8eabc15e20a6",
```
