# [?] Fixing issue where the selected_ratio_button assert was being checked before being corrected for out-of-bounds values. Also fixed issue where the butt

## Summary
Severity: Unknown
Chain: Nano
Component: nanocurrency/nano-node
Published: 2021-08-31
Source: https://github.com/nanocurrency/nano-node/commit/db6c1624c9550b6ac887d8102bfe517b81a7b5c9
Type: security-commit

## Details
Fixing issue where the selected_ratio_button assert was being checked before being corrected for out-of-bounds values. Also fixed issue where the button id was assumed to be the index but it's actually a free-mapping. Changed mapped keys to be actual button index. (#3428)

## Patch
### nano/qt/qt.cpp
```diff
@@ -1765,9 +1765,9 @@ nano_qt::advanced_actions::advanced_actions (nano_qt::wallet & wallet_a) :
 	wallet (wallet_a)
 {
 	ratio_group->addButton (nano_unit);
+	ratio_group->setId (nano_unit, ratio_group->buttons ().size () - 1);
 	ratio_group->addButton (raw_unit);
-	ratio_group->setId (nano_unit, 2);
-	ratio_group->setId (raw_unit, 3);
+	ratio_group->setId (raw_unit, ratio_group->buttons ().size () - 1);
 	scale_layout->addWidget (scale_label);
 	scale_layout->addWidget (nano_unit);
 	scale_layout->addWidget (raw_unit);
@@ -1825,35 +1825,25 @@ nano_qt::advanced_actions::advanced_actions (nano_qt::wallet & wallet_a) :
 	QObject::connect (nano_unit, &QRadioButton::toggled, [this] () {
 		if (nano_unit->isChecked ())
 		{
-			QSettings ().setValue (saved_ratio_key, ratio_group->id (nano_unit));
 			this->wallet.change_rendering_ratio (nano::Mxrb_ratio);
+			QSettings ().setValue (saved_ratio_key, ratio_group->id (nano_unit));
 		}
 	});
 	QObject::connect (raw_unit, &QRadioButton::toggled, [this] () {
 		if (raw_unit->isChecked ())
 		{
-			QSettings ().setValue (saved_ratio_key, ratio_group->id (raw_unit));
 			this->wallet.change_rendering_ratio (nano::raw_ratio);
+			QSettings ().setValue (saved_ratio_key, ratio_group->id (raw_unit));
 		}
 	});
-	auto selected_ratio_id (QSettings ().value (saved_ratio_key, ratio_group->id (nano_unit)).toInt ());
-	auto selected_ratio_button = ratio_group->button (selected_ratio_id);
-	debug_assert (selected_ratio_button != nullptr);
-
-	// Make sure value is not out of bounds
-	if (selected_ratio_id < 0 || selected_ratio_id > 1)
+	auto selected_ratio_button = ratio_group->button (QSettings ().value (saved_ratio_key).toInt ());
+	if (selected_ratio_button == nullptr)
 	{
-		QSettings ().setValue (saved_ratio_key, 0);
-		selected_ratio_id = 0;
-	}
-	if (selected_ratio_button)
-	{
-		selected_ratio_button->click ();
-	}
-	else
-	{
-		nano_unit->click ();
+		selected_ratio_button = nano_unit;
 	}
+	debug_assert (selected_ratio_button != nullptr);
+	selected_ratio_button->click ();
+	QSettings ().setValue (saved_ratio_key, ratio_group->id (selected_ratio_button));
 	QObject::connect (wallet_refresh, &QPushButton::released, [this] () {
 		this->wallet.accounts.refresh ();
 		this->wallet.accounts.refresh_wallet_balance ();
```
