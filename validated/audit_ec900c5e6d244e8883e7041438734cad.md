## Analysis

The reference bug class is: a value is computed/used in multiple places, but binding/validation of that value is only enforced along one code path (or, per the rules, "a field acted on but not covered by the HMAC"). The strongest analog in `lib/shopify_api/**` is the webhook HMAC verification in `lib/shopify_api/webhooks/request.rb` and `lib/shopify_api/webhooks/registry.rb`.

`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Webhooks::Request#shop` is read from the unauthenticated `x-shopify-shop-domain`/`shopify-shop-domain` header, which is never included in the signable string: [2](#0-1) 

`HmacValidator.validate` verifies `verifiable_query.hmac` against `verifiable_query.to_signable_string` only — i.e., it authenticates the body bytes, never the shop identifier: [3](#0-2) 

`Registry.process` gates on `HmacValidator.validate(request)` and then forwards `request.shop` — the unauthenticated header value — directly to the handler as the tenant identifier: [4](#0-3) 

This is the exact class of flaw described in the report: `shop` (the field acted on / the tenant/session key) is not covered by the HMAC, while only the raw body is validated. Since a Shopify app has a single `api_secret_key` shared across every merchant installation of that app, an attacker who legitimately installs the app on their own store can capture a genuinely-signed `(raw_body, hmac)` pair from a real webhook sent to their own endpoint, then replay that exact body+HMAC to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header with a victim shop's domain. `HmacValidator.validate` still succeeds (it only checks body integrity against the shared secret), and `WebhookMetadata.new(shop: request.shop, ...)` binds the forged/replayed payload to the victim's shop when handed to the host application's handler.

### Title
Webhook HMAC does not bind the `shop` identifier, enabling cross-tenant webhook forgery via replay - (File: lib/shopify_api/webhooks/request.rb, lib/shopify_api/webhooks/registry.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` only returns the raw body, and `HmacValidator.validate` only authenticates that raw body against the shared `api_secret_key`. The `shop` (tenant identifier) taken from the `x-shopify-shop-domain` header is never included in the HMAC-covered data, so it is trusted without being cryptographically bound to the signed payload.

### Finding Description
`Registry.process` treats a webhook as authentic solely because `Utils::HmacValidator.validate(request)` passes: [5](#0-4) 
That validation only proves the raw body was produced by someone holding `api_secret_key` — it says nothing about which shop the request is "for," because `to_signable_string` excludes the `shop` header: [1](#0-0) 
Because `api_secret_key` is a single value shared by the app across all merchant installations (not per-shop), any party who has legitimately installed the app on their own store can obtain a validly-signed `(body, hmac)` pair from their own webhook deliveries, and replay it to the app's webhook endpoint with an arbitrary `x-shopify-shop-domain` header. `HmacValidator.validate` will still return `true`, and the unauthenticated `shop` value flows straight into `WebhookMetadata` used by the host app's handler: [6](#0-5) 
This breaks the intended identity binding: `shop authenticated by HMAC` should equal `shop the handler/host app treats as the event's tenant`, but the gem allows these to diverge.

### Impact Explanation
Host applications built on this gem commonly use `WebhookMetadata#shop` to look up a stored session/access token and to scope data mutations (e.g., delete a resource, update local state) for "the shop the webhook is about." An attacker who can forge the shop identifier while keeping a valid HMAC can inject events attributed to a victim shop, causing the host app to act on/for that victim tenant using the app's stored access token for that shop — i.e., cross-tenant access/action, which maps to the Critical/High bucket (cross-tenant access) in the rules.

### Likelihood Explanation
Requires the attacker to be a legitimate (even trial) installer of the same app on their own store to harvest one valid `(body, hmac)` pair — a normal, low-privilege path available to "any unprivileged internet user" who can install a public Shopify app. No access to `api_secret_key`, tokens, or victim credentials is needed.

### Recommendation
Include the shop domain (and ideally topic/webhook id) in the value that is HMAC-verified, or independently verify that `request.shop` corresponds to a shop with an active, matching webhook registration before dispatching to handlers. At minimum, document/enforce that host apps must not trust `WebhookMetadata#shop` for tenant scoping without additional verification (e.g., cross-checking against the known set of installed shops before using it as a session lookup key).

### Proof of Concept
1. Install the target app on attacker-controlled shop `attacker.myshopify.com`; trigger a webhook event to receive a real `(raw_body, x-shopify-hmac-sha256)` pair signed with the app's shared `api_secret_key`.
2. POST that same `raw_body` and `x-shopify-hmac-sha256` value to the app's webhook endpoint, but set `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses headers, `Registry.process` calls `HmacValidator.validate`, which succeeds because only `raw_body` is checked: [7](#0-6) 
4. The handler receives `WebhookMetadata` with `shop: "victim.myshopify.com"` and acts on the victim tenant using attacker-supplied body content.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
      end
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery).returns(T::Boolean) }
        def validate(verifiable_query)
          return false unless verifiable_query.hmac

          result = validate_signature(verifiable_query, Context.api_secret_key)
          if result || Context.old_api_secret_key.nil? || T.must(Context.old_api_secret_key).empty?
            result
          else
            validate_signature(verifiable_query, T.must(Context.old_api_secret_key))
          end
        end

        private

        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/registry.rb (L188-200)
```ruby
        sig { params(request: Request).void }
        def process(request)
          raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)

          handler = @registry[request.topic]&.handler

          unless handler
            raise Errors::NoWebhookHandler, "No webhook handler found for topic: #{request.topic}."
          end

          handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
            body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
        end
```
