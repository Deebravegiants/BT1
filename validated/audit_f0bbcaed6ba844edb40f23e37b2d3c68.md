## Title
Webhook shop identity (`shopify-shop-domain`/`topic` headers) is not covered by the HMAC signature, allowing cross-tenant shop-attribution spoofing in `ShopifyAPI::Webhooks::Registry.process` - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , while `shop`, `topic`, `api_version`, and `webhook_id` are all read from unauthenticated HTTP headers [2](#0-1) . `Registry.process` validates only the HMAC over the body and then trusts `request.shop`/`request.topic` verbatim to dispatch the payload to the app's handler [3](#0-2) . This breaks the identity binding `shop_that_produced_the_HMAC == shop_attributed_to_the_payload_by_the_handler`.

### Finding Description
Shopify signs webhook deliveries with a single, app-wide HMAC secret (`Context.api_secret_key`) computed over the raw JSON body only; the `shop-domain` and `topic` headers are never part of the signed material. `HmacValidator.validate` simply recomputes the signature over `to_signable_string` (the raw body) and compares it to the received HMAC [4](#0-3) . Because the same secret is shared across every shop that has the app installed, a party controlling one merchant shop can capture a legitimate `(raw_body, hmac)` pair delivered to their own shop and replay it to the app's webhook endpoint with the `shopify-shop-domain` header swapped to a different, victim shop. The HMAC still validates (it only ever covered the body), and `Registry.process` forwards `request.shop` (attacker-chosen) together with `request.parsed_body` (attacker's own shop's data) straight to the registered `WebhookHandler` as if it legitimately originated from the victim shop [5](#0-4) .

The `Request` constructor only enforces the presence of the headers, not their integrity [6](#0-5) , and the test suite explicitly documents this by constructing arbitrary `shopify-shop-domain` values independent of the HMAC [7](#0-6) .

### Impact Explanation
This crosses a tenant boundary inside the host application: whatever code the developer wires up via `WebhookHandler#handle` (e.g., updating per-shop billing state, provisioning resources, writing to a shop-keyed datastore, revoking/granting access) will act under the attacker-supplied `shop` identity while consuming attacker-supplied body content, all while passing the gem's own signature check. Depending on how the handler keys its side effects, this enables cross-tenant data injection/confusion — e.g. forging a `shop/redact` or `app/uninstalled` webhook attributed to a victim shop, or injecting arbitrary order/customer payloads "as" the victim shop. This satisfies the High-severity "scope/expiry check bypass"-class impact (identity-binding bypass across tenants) requested by the rules, since the app has no way, within this gem, to prove the header-derived `shop` actually matches the shop whose secret produced the HMAC.

### Likelihood Explanation
Requires the attacker to control (or briefly install the target app on) at least one shop to obtain a valid `(body, hmac)` pair — no `api_secret_key`, access token, or other Shopify credential leak is required, and no host-application misuse is needed: the vulnerable trust decision (accepting the header `shop` without binding it to the HMAC) is made entirely inside this gem's `Webhooks::Request`/`Registry.process`. Any app author who follows the documented `Registry.process` API and keys behavior off `WebhookMetadata#shop` is exposed automatically.

### Recommendation
Bind `shop` (and ideally `topic`, `api_version`, `webhook_id`) into the signed material verified by `to_signable_string`, or otherwise cryptographically tie the header values to the signed body (e.g., include a canonicalized header+body string in the HMAC check, or require the app to separately verify `shop` against its own installation record before trusting the payload). At minimum, document prominently that `request.shop`/`request.topic` are NOT covered by HMAC verification and must not be trusted for authorization decisions without an independent lookup.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com`, triggering a legitimate webhook, e.g. `orders/create`, delivered with headers:
   - `X-Shopify-Topic: orders/create`
   - `X-Shopify-Hmac-Sha256: <valid HMAC of raw_body>`
   - `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`
   and some `raw_body` JSON.
2. Attacker captures `raw_body` and the valid `hmac` value.
3. Attacker replays the identical `raw_body`/`hmac` to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate(request)` recomputes the HMAC over `raw_body` only [8](#0-7)  — it matches, since `shop` was never part of the signed string.
5. `Registry.process` calls the handler with `shop: "victim-shop.myshopify.com"` and `body:` equal to the attacker's own order data [9](#0-8) , causing the app to process/attribute attacker-controlled data as belonging to the victim shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-33)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end

      sig { returns(String) }
      def api_version
        T.cast(shopify_header("api-version"), String)
      end

      sig { returns(String) }
      def webhook_id
        T.cast(shopify_header("webhook-id"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L45-63)
```ruby
      sig { params(raw_body: String, headers: T::Hash[String, T.untyped]).void }
      def initialize(raw_body:, headers:)
        # normalize the headers by forcing lowercase, removing any prepended "http"s, and changing underscores to dashes
        headers = headers.to_h { |k, v| [k.to_s.downcase.sub("http_", "").gsub("_", "-"), v] }

        missing_headers = []
        ["topic", "hmac-sha256", "shop-domain"].each do |name|
          unless headers.key?("shopify-#{name}") || headers.key?("x-shopify-#{name}")
            missing_headers << "shopify-#{name} or x-shopify-#{name}"
          end
        end
        unless missing_headers.empty?
          raise Errors::InvalidWebhookError,
            "Missing one or more of the required HTTP headers to process webhooks: #{missing_headers}"
        end

        @headers = headers
        @raw_body = raw_body
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
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
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** test/webhooks/registry_test.rb (L284-299)
```ruby
        hmac = OpenSSL::HMAC.digest(
          OpenSSL::Digest.new("sha256"),
          ShopifyAPI::Context.api_secret_key,
          "{}",
        )

        new_format_headers = {
          "shopify-topic" => @topic,
          "shopify-hmac-sha256" => Base64.encode64(hmac),
          "shopify-shop-domain" => @shop,
          "shopify-webhook-id" => "b1234-eefd-4c9e-9520-049845a02082",
          "shopify-api-version" => "2024-01",
        }

        webhook_request = ShopifyAPI::Webhooks::Request.new(raw_body: "{}", headers: new_format_headers)
        ShopifyAPI::Webhooks::Registry.process(webhook_request)
```
