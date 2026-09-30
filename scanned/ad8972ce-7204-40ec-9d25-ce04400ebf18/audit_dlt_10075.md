# [?] Fix crash in nano_wallet when ran with --config option (#3546)

## Summary
Severity: Unknown
Chain: Nano
Component: nanocurrency/nano-node
Published: 2021-11-05
Source: https://github.com/nanocurrency/nano-node/commit/a063100a0c1dc3e279dadd029d6405dd810768d0
Type: security-commit

## Details
Fix crash in nano_wallet when ran with --config option (#3546)

## Patch
### nano/nano_wallet/entry.cpp
```diff
@@ -74,11 +74,11 @@ int run_wallet (QApplication & application, int argc, char * const * argv, boost
 	boost::filesystem::create_directories (data_path);
 	nano::set_secure_perm_directory (data_path, error_chmod);
 	QPixmap pixmap (":/logo.png");
-	QSplashScreen * splash = new QSplashScreen (pixmap);
+	auto * splash = new QSplashScreen (pixmap);
 	splash->show ();
-	application.processEvents ();
+	QApplication::processEvents ();
 	splash->showMessage (QSplashScreen::tr ("Remember - Back Up Your Wallet Seed"), Qt::AlignBottom | Qt::AlignHCenter, Qt::darkGray);
-	application.processEvents ();
+	QApplication::processEvents ();
 
 	nano::network_params network_params{ nano::network_constants::active_network };
 	nano::daemon_config config{ data_path, network_params };
@@ -184,7 +184,7 @@ int run_wallet (QApplication & application, int argc, char * const * argv, boost
 				{
 					// Launch rpc in-process
 					nano::rpc_config rpc_config{ config.node.network_params.network };
-					auto error = nano::read_rpc_config_toml (data_path, rpc_config, flags.rpc_config_overrides);
+					error = nano::read_rpc_config_toml (data_path, rpc_config, flags.rpc_config_overrides);
 					if (error)
 					{
 						splash->hide ();
@@ -228,13 +228,13 @@ int run_wallet (QApplication & application, int argc, char * const * argv, boost
 #endif
 				runner.stop_event_processing ();
 			});
-			application.postEvent (&processor, new nano_qt::eventloop_event ([&] () {
+			QApplication::postEvent (&processor, new nano_qt::eventloop_event ([&] () {
 				gui = std::make_shared<nano_qt::wallet> (application, processor, *node, wallet, wallet_config.account);
 				splash->close ();
 				gui->start ();
 				gui->client_window->show ();
 			}));
-			result = application.exec ();
+			result = QApplication::exec ();
 			runner.join ();
 		}
 		else
@@ -256,9 +256,11 @@ int main (int argc, char * const * argv)
 {
 	nano::set_umask ();
 	nano::node_singleton_memory_pool_purge_guard memory_pool_cleanup_guard;
+
+	QApplication application (argc, const_cast<char **> (argv));
+
 	try
 	{
-		QApplication application (argc, const_cast<char **> (argv));
 		boost::program_options::options_description description ("Command line options");
 		// clang-format off
 		description.add_options()
@@ -292,9 +294,10 @@ int main (int argc, char * const * argv)
 		}
 
 		std::vector<std::string> config_overrides;
-		if (vm.count ("config"))
+		const auto configItr = vm.find ("config");
+		if (configItr != vm.cend ())
 		{
-			config_overrides = vm["config"].as<std::vector<std::string>> ();
+			config_overrides = nano::config_overrides (configItr->second.as<std::vector<nano::config_key_value_pair>> ());
 		}
 
 		auto ec = nano::handle_node_options (vm);
```
