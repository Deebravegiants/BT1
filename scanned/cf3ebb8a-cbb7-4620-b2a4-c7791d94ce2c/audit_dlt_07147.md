# [?] Merge bitcoin/bitcoin#36176: wallet: avoid a crash when creating a wallet with -nosettings

## Summary
Severity: Unknown
Chain: Bitcoin
Component: bitcoin/bitcoin
Published: 2026-09-07
Source: https://github.com/bitcoin/bitcoin/commit/013b0b2de48153b7481c036a353b81a411f1da8f
Type: security-commit

## Details
Merge bitcoin/bitcoin#36176: wallet: avoid a crash when creating a wallet with -nosettings

a34fc8b11a420c1ed9877a5dd73aab57aba17cd0 wallet: handle disabled startup settings (Robert Hamilton)
b7113e6f42c220792c2a9808943b714eb72c4f3e test: characterize disabled wallet settings (Robert Hamilton)

Pull request description:

  I hit a crash while creating a new wallet in Bitcoin-Qt 31.1 on an Apple silicon Mac with `nosettings=1`. After looking through the crash report and code, I traced it to saving the wallet's load-on-startup setting: the settings writer throws when dynamic settings are disabled.

  Wallet RPCs report errors with `-nosettings` after changing wallet state. In Qt, the same settings write causes an uncaught exception.

  Return a persistence failure when dynamic settings are disabled so wallet operations finish with their existing startup-setting warning. This avoids an uncaught exception in Qt and RPC errors after the wallet state has already changed. Keep in-memory and no-op updates unchanged.

  The first commit adds functional coverage for the current behavior. The second adds the fix, updates the assertions to expect success with warnings, and documents that failed settings writes keep the in-memory changes.

  ### Manual Reproduction

  Run on the parent commit and the fixed commit, using a fresh temporary regtest data directory each time:

  ```sh
  { cmake -B build-wallet-review -DBUILD_GUI=ON && cmake --build build-wallet-review -j --target bitcoin-qt; } >/dev/null 2>&1
  build-wallet-review/bin/bitcoin-qt -regtest -datadir="$(mktemp -d)" -nosettings -noconnect
  ```

  Choose `File` > `Create Wallet...`, enter `repro`, leave the defaults unchanged, and click `Create`.

  Before the fix, the application terminates with:

  ```text
  libc++abi: terminating due to uncaught exception of type std::logic_error: Attempt to write settings file when dynamic settings are disabled.
  ```

  After the fix, the wallet is created and the application displays:

  ```text
  Wallet load on startup setting could not be updated, so wallet may not be loaded next node startup.
  ```

ACKs for top commit:
  l0rinc:
    tested ACK a34fc8b11a420c1ed9877a5dd73aab57aba17cd0
  kevkevinpal:
    tACK a34fc8b11a420c1ed9877a5dd73aab57aba17cd0
  achow101:
    ACK a34fc8b11a420c1ed9877a5dd73aab57aba17cd0
  jeanpablojp:
    tACK a34fc8b11a420c1ed9877a5dd73aab57aba17cd0

Tree-SHA512: 5e43028200478f89e71ebe7e0fc28c559f15e713226124899a69eb90d413d8ecaaaca02267d5a848068d70555b3e4334993f414de2debf6a22d73a51a71d1acd

## Patch
### src/interfaces/chain.h
```diff
@@ -358,6 +358,9 @@ class Chain
     //! support for writing null values to settings.json.
     //! Depending on the action returned by the update function, this will either
     //! update the setting in memory or write the updated settings to disk.
+    //! Returns false if the update function returned no action, or if the
+    //! settings could not be written to disk, including when settings are
+    //! disabled with -nosettings. In-memory changes are kept either way.
     virtual bool updateRwSetting(const std::string& name, const SettingsUpdate& update_function) = 0;
 
     //! Replace a setting in <datadir>/settings.json with a new value.
```

### src/node/interfaces.cpp
```diff
@@ -843,7 +843,7 @@ class ChainImpl : public Chain
         });
         if (!action) return false;
         // Now dump value to disk if requested
-        return *action != interfaces::SettingsAction::WRITE || args().WriteSettingsFile();
+        return *action != interfaces::SettingsAction::WRITE || (args().GetSettingsPath() && args().WriteSettingsFile());
     }
     bool overwriteRwSetting(const std::string& name, common::SettingsValue value, interfaces::SettingsAction action) override
     {
```

### test/functional/wallet_startup.py
```diff
@@ -64,6 +64,35 @@ def test_load_unwritable_wallet(self, node):
         # Reset directory permissions for cleanup
         dir_path.chmod(original_dir_perms)
 
+    def test_disabled_settings(self, node):
+        self.log.info("Test wallet startup preferences with dynamic settings disabled")
+        load_message = "Wallet load on startup setting could not be updated, so wallet may not be loaded next node startup."
+
+        settings_path = node.chain_path / "settings.json"
+        settings_before = settings_path.read_bytes()
+        self.restart_node(0, extra_args=["-nosettings"])
+        assert_equal(node.listwallets(), [''])
+
+        assert_equal(node.createwallet(wallet_name="no_settings", load_on_startup=True), {"name": "no_settings", "warnings": [load_message]})
+        assert_equal(set(node.listwallets()), {'', 'no_settings'})
+
+        # Leaving the startup preference unchanged does not warn, and the wallet remains usable.
+        assert_equal(node.unloadwallet(wallet_name="no_settings"), {})
+        assert_equal(node.loadwallet(filename="no_settings"), {"name": "no_settings"})
+        assert_equal(node.get_wallet_rpc("no_settings").getwalletinfo()["walletname"], "no_settings")
+
+        assert_equal(node.loadwallet(filename="w2", load_on_startup=True), {"name": "w2", "warnings": [load_message]})
+        assert_equal(set(node.listwallets()), {'', 'no_settings', 'w2'})
+
+        assert_equal(node.unloadwallet(wallet_name="no_settings", load_on_startup=False), {"warnings": ["Wallet load on startup setting could not be updated, so wallet may still be loaded next node startup."]})
+        assert_equal(set(node.listwallets()), {'', 'w2'})
+        self.stop_node(0)
+        assert_equal(settings_path.read_bytes(), settings_before)
+
+        # Re-enabling settings restores the original startup preferences.
+        self.start_node(0)
+        assert_equal(set(node.listwallets()), {'w2', 'w3'})
+
     def run_test(self):
         self.log.info('Should start without any wallets')
         assert_equal(self.nodes[0].listwallets(), [])
@@ -94,6 +123,7 @@ def run_test(self):
         assert_equal(set(self.nodes[0].listwallets()), set(('w2', 'w3')))
 
         self.test_load_unwritable_wallet(self.nodes[0])
+        self.test_disabled_settings(self.nodes[0])
 
 if __name__ == '__main__':
     WalletStartupTest(__file__).main()
```
