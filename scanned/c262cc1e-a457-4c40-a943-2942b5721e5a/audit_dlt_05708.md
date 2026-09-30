# [?] setconfig: fix crash on dynamic multi-value plugin options

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: ElementsProject/lightning
Published: 2026-05-11
Source: https://github.com/ElementsProject/lightning/commit/e9fee876d735135e0b939db8271418dc01a27ba7
Type: security-commit

## Details
setconfig: fix crash on dynamic multi-value plugin options

We had an assert(!(ot->type & OPT_MULTI)) which crashed when using
setconfig on a plugin option marked as both dynamic and multi.

The fix changes plugin_set_dynamic_opt to accept an array of values
(scalar options pass a 1-element array, multi options pass the complete
set). For multi options, setconfig replaces ALL values atomically - an
empty array clears them.

Fixes: #8295

Changelog-Fixed: setconfig no longer crashes on dynamic multi-value plugin options

## Patch
### .msggen.json
```diff
@@ -4060,10 +4060,12 @@
             "SetConfig.config.plugin": 3,
             "SetConfig.config.set": 5,
             "SetConfig.config.source": 2,
+            "SetConfig.config.sources[]": 10,
             "SetConfig.config.value_bool": 9,
             "SetConfig.config.value_int": 8,
             "SetConfig.config.value_msat": 7,
-            "SetConfig.config.value_str": 6
+            "SetConfig.config.value_str": 6,
+            "SetConfig.config.values_str[]": 11
         },
         "SetconfigRequest": {
             "SetConfig.config": 1,
@@ -13757,6 +13759,10 @@
             "added": "v23.08",
             "deprecated": null
         },
+        "SetConfig.config.sources[]": {
+            "added": "v26.06",
+            "deprecated": null
+        },
         "SetConfig.config.value_bool": {
             "added": "v23.08",
             "deprecated": null
@@ -13773,6 +13779,10 @@
             "added": "v23.08",
             "deprecated": null
         },
+        "SetConfig.config.values_str[]": {
+            "added": "v26.06",
+            "deprecated": null
+        },
         "SetConfig.transient": {
             "added": "v25.02",
             "deprecated": null
```

### cln-grpc/proto/node.proto
```diff
@@ -2767,14 +2767,16 @@ message SetconfigResponse {
 
 message SetconfigConfig {
 	string config = 1;
-	string source = 2;
+	optional string source = 2;
 	optional string plugin = 3;
 	bool dynamic = 4;
 	optional bool set = 5;
 	optional string value_str = 6;
 	optional Amount value_msat = 7;
 	optional sint64 value_int = 8;
 	optional bool value_bool = 9;
+	repeated string sources = 10;
+	repeated string values_str = 11;
 }
 
 message SetpsbtversionRequest {
```

### cln-grpc/src/convert.rs
```diff
@@ -2572,11 +2572,15 @@ impl From<responses::SetconfigConfig> for pb::SetconfigConfig {
             dynamic: c.dynamic, // Rule #2 for type boolean
             plugin: c.plugin, // Rule #2 for type string?
             set: c.set, // Rule #2 for type boolean?
-            source: c.source, // Rule #2 for type string
+            source: c.source, // Rule #2 for type string?
+            // Field: SetConfig.config.sources[]
+            sources: c.sources.map(|arr| arr.into_iter().map(|i| i.into()).collect()).unwrap_or(vec![]), // Rule #3
             value_bool: c.value_bool, // Rule #2 for type boolean?
             value_int: c.value_int, // Rule #2 for type integer?
             value_msat: c.value_msat.map(|f| f.into()), // Rule #2 for type msat?
             value_str: c.value_str, // Rule #2 for type string?
+            // Field: SetConfig.config.values_str[]
+            values_str: c.values_str.map(|arr| arr.into_iter().map(|i| i.into()).collect()).unwrap_or(vec![]), // Rule #3
         }
     }
 }
```

### cln-rpc/src/model.rs
```diff
@@ -9845,16 +9845,21 @@ pub mod responses {
 	    #[serde(skip_serializing_if = "Option::is_none")]
 	    pub set: Option<bool>,
 	    #[serde(skip_serializing_if = "Option::is_none")]
+	    pub source: Option<String>,
+	    #[serde(skip_serializing_if = "Option::is_none")]
 	    pub value_bool: Option<bool>,
 	    #[serde(skip_serializing_if = "Option::is_none")]
 	    pub value_int: Option<i64>,
 	    #[serde(skip_serializing_if = "Option::is_none")]
 	    pub value_msat: Option<Amount>,
 	    #[serde(skip_serializing_if = "Option::is_none")]
 	    pub value_str: Option<String>,
+	    #[serde(skip_serializing_if = "crate::is_none_or_empty")]
+	    pub sources: Option<Vec<String>>,
+	    #[serde(skip_serializing_if = "crate::is_none_or_empty")]
+	    pub values_str: Option<Vec<String>>,
 	    pub config: String,
 	    pub dynamic: bool,
-	    pub source: String,
 	}
 
 	#[derive(Clone, Debug, Deserialize, Serialize)]
```

### common/configvar.c
```diff
@@ -107,9 +107,18 @@ void configvar_finalize_overrides(struct configvar **cvs)
 	opts = tal_arr(tmpctx, const struct opt_table *, tal_count(cvs));
 	for (size_t i = 0; i < tal_count(cvs); i++) {
 		opts[i] = opt_find_long(cvs[i]->optvar, NULL);
-		/* If you're allowed multiple, they don't override */
-		if (opts[i]->type & OPT_MULTI)
+		/* If you're allowed multiple, they don't override...
+		 * unless transient values exist, which override non-transient. */
+		if (opts[i]->type & OPT_MULTI) {
+			if (cvs[i]->src != CONFIGVAR_SETCONFIG_TRANSIENT)
+				continue;
+			for (size_t j = 0; j < i; j++) {
+				if (opts[j] == opts[i] &&
+				    cvs[j]->src != CONFIGVAR_SETCONFIG_TRANSIENT)
+					cvs[j]->overridden = true;
+			}
 			continue;
+		}
 		for (size_t j = 0; j < i; j++) {
 			if (opts[j] == opts[i])
 				cvs[j]->overridden = true;
```

### contrib/msggen/msggen/schema.json
```diff
@@ -33890,10 +33890,19 @@
               },
               {
                 "type": "boolean"
+              },
+              {
+                "type": "array",
+                "items": {
+                  "type": "string"
+                },
+                "description": [
+                  "For multi options, an array of string values."
+                ]
               }
             ],
             "description": [
-              "Value of the config variable to be set or updated."
+              "Value of the config variable to be set or updated. For multi options, this must be an array of strings."
             ]
           },
           "transient": {
@@ -33920,7 +33929,6 @@
             "additionalProperties": false,
             "required": [
               "config",
-              "source",
               "dynamic"
             ],
             "properties": {
@@ -33933,7 +33941,17 @@
               "source": {
                 "type": "string",
                 "description": [
-                  "Source of configuration setting (`file`:`linenum`)."
+                  "Source of configuration setting (`file`:`linenum`) for non-multi options."
+                ]
+              },
+              "sources": {
+                "type": "array",
+                "added": "v26.06",
+                "items": {
+                  "type": "string"
+                },
+                "description": [
+                  "Sources of configuration settings (`file`:`linenum`) for multi options."
                 ]
               },
               "plugin": {
@@ -33980,6 +33998,16 @@
                 "description": [
                   "For boolean options."
                 ]
+              },
+              "values_str": {
+                "type": "array",
+                "added": "v26.06",
+                "items": {
+                  "type": "string"
+                },
+                "description": [
+                  "For multi-string options."
+                ]
               }
             }
           }
@@ -34037,6 +34065,37 @@
               "dynamic": true
             }
           }
+        },
+        {
+          "description": [
+            "This shows setting a multi-value dynamic plugin option (requires a plugin that defines such an option)."
+          ],
+          "request": {
+            "id": "example:setconfig#3",
+            "method": "setconfig",
+            "params": {
+              "config": "my-multi-option",
+              "val": [
+                "value1",
+                "value2"
+              ]
+            }
+          },
+          "response": {
+            "config": {
+              "config": "my-multi-option",
+              "values_str": [
+                "value1",
+                "value2"
+              ],
+              "sources": [
+                "/tmp/.lightning/regtest/config.setconfig:4",
+                "/tmp/.lightning/regtest/config.setconfig:5"
+              ],
+              "plugin": "/root/lightning/plugins/myplugin",
+              "dynamic": true
+            }
+          }
         }
       ]
     },
```

### contrib/pyln-testing/pyln/testing/grpc2py.py
```diff
@@ -2015,6 +2015,8 @@ def setchannel2py(m):
 
 def setconfig_config2py(m):
     return remove_default({
+        "sources": [m.sources for i in m.sources], # ArrayField[primitive] in generate_composite
+        "values_str": [m.values_str for i in m.values_str], # ArrayField[primitive] in generate_composite
         "config": m.config,  # PrimitiveField in generate_composite
         "dynamic": m.dynamic,  # PrimitiveField in generate_composite
         "plugin": m.plugin,  # PrimitiveField in generate_composite
```

### doc/schemas/setconfig.json
```diff
@@ -33,10 +33,19 @@
           },
           {
             "type": "boolean"
+          },
+          {
+            "type": "array",
+            "items": {
+              "type": "string"
+            },
+            "description": [
+              "For multi options, an array of string values."
+            ]
           }
         ],
         "description": [
-          "Value of the config variable to be set or updated."
+          "Value of the config variable to be set or updated. For multi options, this must be an array of strings."
         ]
       },
       "transient": {
@@ -63,7 +72,6 @@
         "additionalProperties": false,
         "required": [
           "config",
-          "source",
           "dynamic"
         ],
         "properties": {
@@ -76,7 +84,17 @@
           "source": {
             "type": "string",
             "description": [
-              "Source of configuration setting (`file`:`linenum`)."
+              "Source of configuration setting (`file`:`linenum`) for non-multi options."
+            ]
+          },
+          "sources": {
+            "type": "array",
+            "added": "v26.06",
+            "items": {
+              "type": "string"
+            },
+            "description": [
+              "Sources of configuration settings (`file`:`linenum`) for multi options."
             ]
           },
           "plugin": {
@@ -123,6 +141,16 @@
             "description": [
               "For boolean options."
             ]
+          },
+          "values_str": {
+            "type": "array",
+            "added": "v26.06",
+            "items": {
+              "type": "string"
+            },
+            "description": [
+              "For multi-string options."
+            ]
           }
         }
       }
@@ -180,6 +208,37 @@
           "dynamic": true
         }
       }
+    },
+    {
+      "description": [
+        "This shows setting a multi-value dynamic plugin option (requires a plugin that defines such an option)."
+      ],
+      "request": {
+        "id": "example:setconfig#3",
+        "method": "setconfig",
+        "params": {
+          "config": "my-multi-option",
+          "val": [
+            "value1",
+            "value2"
+          ]
+        }
+      },
+      "response": {
+        "config": {
+          "config": "my-multi-option",
+          "values_str": [
+            "value1",
+            "value2"
+          ],
+          "sources": [
+            "/tmp/.lightning/regtest/config.setconfig:4",
+            "/tmp/.lightning/regtest/config.setconfig:5"
+          ],
+          "plugin": "/root/lightning/plugins/myplugin",
+          "dynamic": true
+        }
+      }
     }
   ]
 }
```

### lightningd/configs.c
```diff
@@ -509,7 +509,6 @@ static void configvar_save(struct lightningd *ld,
 	struct configvar *oldcv;
 	size_t linenum;
 
-	/* If we don't already have "include config.setconfig" add it */
 	if (!ld->setconfig_file)
 		create_setconfig_include(ld);
 
@@ -532,29 +531,76 @@ static void configvar_save(struct lightningd *ld,
 			  ld->setconfig_file, linenum, confline);
 }
 
+/* For multi options: remove all existing, add all new values */
+static void configvar_save_multi(struct lightningd *ld,
+				 const char **names,
+				 const char **conflines,
+				 size_t nvals)
+{
+	size_t linenum;
+
+	if (!ld->setconfig_file)
+		create_setconfig_include(ld);
+
+	/* Comment out all file-based values, even overridden ones. */
+	for (size_t i = 0; i < tal_count(ld->configvars); i++) {
+		struct configvar *cv = ld->configvars[i];
+		if (cv->optvar && streq(cv->optvar, names[0]) && cv->file)
+			configfile_replace_var(ld, cv, NULL);
+	}
+
+	configvar_remove(&ld->configvars, names[0], CONFIGVAR_NETWORK_CONF, NULL);
+
+	for (size_t i = 0; i < nvals; i++) {
+		linenum = append_to_file(ld, ld->setconfig_file, conflines[i], true);
+		configvar_updated(ld, CONFIGVAR_NETWORK_CONF,
+				  ld->setconfig_file, linenum, conflines[i]);
+	}
+}
+
 static struct command_result *setconfig_success(struct command *cmd,
 						const struct opt_table *ot,
-						const char *val,
+						const char **vals,
+						size_t nvals,
 						bool transient)
 {
 	struct json_stream *response;
-	const char **names, *confline;
+	const char **names;
 
 	if (command_check_only(cmd))
 		return command_check_done(cmd);
 
 	names = opt_names_arr(tmpctx, ot);
 
-	if (val)
-		confline = tal_fmt(tmpctx, "%s=%s", names[0], val);
-	else
-		confline = names[0];
+	if (ot->type & OPT_MULTI) {
+		const char **conflines = tal_arr(tmpctx, const char *, nvals);
+		for (size_t i = 0; i < nvals; i++)
+			conflines[i] = tal_fmt(conflines, "%s=%s", names[0], vals[i]);
+
+		/* Always remove old transient values first */
+		configvar_remove(&cmd->ld->configvars, names[0],
+				 CONFIGVAR_SETCONFIG_TRANSIENT, NULL);
+
+		if (!transient) {
+			configvar_save_multi(cmd->ld, names, conflines, nvals);
+		} else {
+			for (size_t i = 0; i < nvals; i++)
+				configvar_updated(cmd->ld, CONFIGVAR_SETCONFIG_TRANSIENT,
+						  NULL, 0, conflines[i]);
+		}
+	} else {
+		const char *confline;
 
-	if (!transient)
-		configvar_save(cmd->ld, names, confline);
-	else
-		configvar_updated(cmd->ld, CONFIGVAR_SETCONFIG_TRANSIENT, NULL, 0, confline);
+		if (nvals > 0 && vals[0])
+			confline = tal_fmt(tmpctx, "%s=%s", names[0], vals[0]);
+		else
+			confline = names[0];
 
+		if (!transient)
+			configvar_save(cmd->ld, names, confline);
+		else
+			configvar_updated(cmd->ld, CONFIGVAR_SETCONFIG_TRANSIENT, NULL, 0, confline);
+	}
 
 	response = json_stream_success(cmd);
 	json_object_start(response, "config");
@@ -613,6 +659,7 @@ static struct command_result *json_setconfig(struct command *cmd,
 	char *err;
 	void *arg;
 	bool *transient;
+	const jsmntok_t *valtok;
 
 	if (!param_check(cmd, buffer, params,
 			 p_req("config", param_opt_dynamic_config, &ot),
@@ -621,8 +668,72 @@ static struct command_result *json_setconfig(struct command *cmd,
 			 NULL))
 		return command_param_failed();
 
-	/* We don't handle DYNAMIC MULTI, at least yet! */
-	assert(!(ot->type & OPT_MULTI));
+	valtok = json_get_member(buffer, params, "val");
+
+	if (ot->type & OPT_MULTI) {
+		const char **vals;
+		const char **names;
+		const jsmntok_t *t;
+		size_t i;
+
+		names = opt_names_arr(tmpctx, ot);
+
+		if (valtok && valtok->type != JSMN_ARRAY)
+			return command_fail(cmd, JSONRPC2_INVALID_PARAMS,
+					    "%s is a multi option: val must be an array",
+					    ot->names + 2);
+
+		if (valtok) {
+			vals = tal_arr(cmd, const char *, valtok->size);
+			json_for_each_arr(i, t, valtok) {
+				vals[i] = json_strdup(vals, buffer, t);
+			}
+		} else {
+			/* No val means empty array (clear all) */
+			vals = tal_arr(cmd, const char *, 0);
+		}
+
+		if (!*transient) {
+			const struct configvar *cv;
+			const char *fname;
+
+			cv = configvar_first(cmd->ld->configvars, names);
+
+			fname = config_not_writable(cmd, cmd, cv);
+			if (fname)
+				return command_fail(cmd, JSONRPC2_INVALID_PARAMS,
+						    "Cannot write to config file %s",
+						    fname);
+
+			/* Check ALL existing config lines haven't changed */
+			for (cv = configvar_first(cmd->ld->configvars, names);
+			     cv;
+			     cv = configvar_next(cmd->ld->configvars, cv, names)) {
+				if (cv->file) {
+					const char *changed;
+					char **lines;
+
+					changed = grab_and_check(tmpctx,
+								 cv->file, cv->linenum,
+								 cv->configline,
+								 &lines);
+					if (changed)
+						return command_fail(cmd, JSONRPC2_INVALID_PARAMS,
+								    "%s", changed);
+				}
+			}
+		}
+
+		/* Multi options are always plugin options */
+		assert(is_plugin_opt(ot));
+		return plugin_set_dynamic_opt(cmd, ot, vals, tal_count(vals),
+					      *transient, setconfig_success);
+	}
+
+	if (valtok && valtok->type == JSMN_ARRAY)
+		return command_fail(cmd, JSONRPC2_INVALID_PARAMS,
+				    "%s is not a multi option: val must not be an array",
+				    ot->names + 2);
 
 	if (!*transient) {
 		const struct configvar *cv;
@@ -665,18 +776,21 @@ static struct command_result *json_setconfig(struct command *cmd,
 					    "%s does not take a value",
 					    ot->names + 2);
 		if (is_plugin_opt(ot))
-			return plugin_set_dynamic_opt(cmd, ot, NULL, *transient,
-						      setconfig_success);
+			return plugin_set_dynamic_opt(cmd, ot, NULL, 0,
+						      *transient, setconfig_success);
 		err = ot->cb(arg);
 	} else {
 		assert(ot->type & OPT_HASARG);
 		if (!val)
 			return command_fail(cmd, JSONRPC2_INVALID_PARAMS,
 					    "%s requires a value",
 					    ot->names + 2);
-		if (is_plugin_opt(ot))
-			return plugin_set_dynamic_opt(cmd, ot, val, *transient,
-						      setconfig_success);
+		if (is_plugin_opt(ot)) {
+			const char **vals = tal_arr(cmd, const char *, 1);
+			vals[0] = val;
+			return plugin_set_dynamic_opt(cmd, ot, vals, 1,
+						      *transient, setconfig_success);
+		}
 		err = ot->cb_arg(val, arg);
 	}
 
@@ -685,7 +799,10 @@ static struct command_result *json_setconfig(struct command *cmd,
 				    "Error setting %s: %s", ot->names + 2, err);
 	}
 
-	return setconfig_success(cmd, ot, val, *transient);
+	{
+		const char *vals[1] = {val};
+		return setconfig_success(cmd, ot, val ? vals : NULL, val ? 1 : 0, *transient);
+	}
 }
 
 static const struct json_command setconfig_command = {
```

### lightningd/plugin.c
```diff
@@ -2231,12 +2231,14 @@ bool plugins_config(struct plugins *plugins)
 
 struct plugin_set_return {
 	struct command *cmd;
-	const char *val;
+	const char **vals;
+	size_t nvals;
 	const char *optname;
 	bool transient;
 	struct command_result *(*success)(struct command *,
 					  const struct opt_table *,
-					  const char *,
+					  const char **,
+					  size_t,
 					  bool);
 };
 
@@ -2278,7 +2280,7 @@ static void plugin_setconfig_done(const char *buffer,
 	t = json_get_member(buffer, toks, "result");
 	if (!t)
 		goto bad_response;
-	was_pending(psr->success(psr->cmd, ot, psr->val, psr->transient));
+	was_pending(psr->success(psr->cmd, ot, psr->vals, psr->nvals, psr->transient));
 	return;
 
 bad_response:
@@ -2292,12 +2294,14 @@ static void plugin_setconfig_done(const char *buffer,
 
 struct command_result *plugin_set_dynamic_opt(struct command *cmd,
 					      const struct opt_table *ot,
-					      const char *val,
+					      const char **vals,
+					      size_t nvals,
 					      bool transient,
 					      struct command_result *(*success)
 					      (struct command *,
 					       const struct opt_table *,
-					       const char *,
+					       const char **,
+					       size_t,
 					       bool))
 {
 	struct plugin_opt *popt;
@@ -2312,8 +2316,9 @@ struct command_result *plugin_set_dynamic_opt(struct command *cmd,
 
 	psr = tal(cmd, struct plugin_set_return);
 	psr->cmd = cmd;
-	/* val is a child of cmd, so no copy needed. */
-	psr->val = val;
+	/* vals is a child of cmd, so no copy needed. */
+	psr->vals = vals;
+	psr->nvals = nvals;
 	psr->optname = tal_strdup(psr, ot->names + 2);
 	psr->success = success;
 	psr->transient = transient;
@@ -2336,8 +2341,15 @@ struct command_result *plugin_set_dynamic_opt(struct command *cmd,
 					    psr);
 	}
 	json_add_string(req->stream, "config", psr->optname);
-	if (psr->val)
-		json_add_string(req->stream, "val", psr->val);
+	/* Multi options: send array. Scalar: send single value or nothing. */
+	if (ot->type & OPT_MULTI) {
+		json_array_start(req->stream, "val");
+		for (size_t i = 0; i < nvals; i++)
+			json_add_string(req->stream, NULL, vals[i]);
+		json_array_end(req->stream);
+	} else if (nvals > 0 && vals[0]) {
+		json_add_string(req->stream, "val", vals[0]);
+	}
 	jsonrpc_request_end(req);
 	plugin_request_send(plugin, req);
 	return command_still_pending(cmd);
```

### lightningd/plugin.h
```diff
@@ -407,15 +407,19 @@ void json_add_config_plugin(struct json_stream *stream,
 			    const char *fieldname,
 			    const struct opt_table *ot);
 
-/* Attempt to setconfig an option in a plugin.  Calls success or fail, may be async! */
+/* Attempt to setconfig an option in a plugin.  Calls success or fail, may be async!
+ * For scalar options: vals is 1-element array (or NULL/0 for NOARG).
+ * For multi options: vals is the complete new set of values. */
 struct command_result *plugin_set_dynamic_opt(struct command *cmd,
 					      const struct opt_table *ot,
-					      const char *val,
+					      const char **vals,
+					      size_t nvals,
 					      bool transient,
 					      struct command_result *(*success)
 					      (struct command *,
 					       const struct opt_table *,
-					       const char *,
+					       const char **,
+					       size_t,
 					       bool));
 
 /* --dev-plugin-save-io */
```
