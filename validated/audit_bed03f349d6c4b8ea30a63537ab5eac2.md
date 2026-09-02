### Title
Webhook Request Shop/Topic/Metadata Not Covered by HMAC Allows Cross-Tenant Webhook Spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw body only, while the `shop`, `topic`, `api_version`, and `webhook_id` values used by `ShopifyAPI::Webhooks::Registry.process` are read from unauthenticated HTTP headers that are never included in the signed payload. An attacker who possesses one genuine `(raw_body, hmac)` pair (trivially obtainable by installing the app on their own store and receiving a real webhook) can replay that exact body/HMAC combination while freely rewriting the `x-shopify-shop-domain` (and `topic`/`webhook-id`/`api-version`) headers, and the signature check still passes.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

but `shop`, `topic`, `api_version`, and `webhook_id` are all pulled straight from attacker-controlled headers with no cryptographic binding: [2](#0-1) 

`Utils::HmacValidator.validate` only verifies `request.hmac` against `request.to_signable_string` (i.e., the raw body) using the app's `api_secret_key`: [3](#0-2) 

`Webhooks::Registry.process` then trusts the unauthenticated `request.shop` field once the (body-only) HMAC passes, and forwards it to the app's handler as the identity of the originating shop: [4](#0-3) 

This breaks the identity binding: `shop authenticated by HMAC` (∅, nothing) ≠ `shop trusted by application logic` (`request.shop`, taken from the unauthenticated `x-shopify-shop-domain`/`shopify-shop-domain` header). Any unprivileged internet user who can install the app on a store they control (or otherwise capture one valid `(body, hmac)` pair for any topic) can:
1. Capture a legitimate webhook delivery to their own shop's endpoint (valid body + valid HMAC signed with the shared `api_secret_key`).
2. Replay the identical body/HMAC to the app's webhook endpoint while substituting `x-shopify-shop-domain` (and optionally `x-shopify-topic`/`x-shopify-webhook-id`) with an arbitrary victim shop's domain.
3. `HmacValidator.validate` still succeeds because it only checks the raw body, and `Registry.process` dispatches the handler with `shop: request.shop` set to the forged victim domain.

The test suite confirms the signable string is body-only and that `shop` is derived purely from the header: [5](#0-4) 

### Impact Explanation
This is a cross-tenant identity-binding break: the application-level webhook handler receives forged events attributed to a shop the attacker does not control, using only a valid HMAC obtained from the attacker's own (or any) shop. Any host application logic that trusts `WebhookMetadata#shop` to select which merchant's data/tenant record to update, delete, or sync (a standard pattern for webhook consumers) can be manipulated into applying attacker-controlled data under a victim merchant's identity — a cross-tenant access/injection primitive entirely enabled by this gem's failure to bind the shop domain into the signed material.

### Likelihood Explanation
High. No leaked credentials, access tokens, or `api_secret_key` are needed. An attacker only needs the ability to receive one legitimate webhook delivery (e.g. by installing the app on any store, including a free development store) to obtain a valid `(raw_body, hmac)` pair, then replay it with a forged `shop-domain` header. The header substitution is a standard HTTP client operation requiring no special access.

### Recommendation
Include `shop`, `topic`, `api_version`, and `webhook_id` in the signed material used for HMAC validation (or, at minimum, provide a way to verify these values against the raw body's own reported shop/topic where Shopify webhook payloads include them), and document/enforce that consumers must not trust header-only fields independent of the signature. Ideally, `to_signable_string` should incorporate all header fields that downstream code treats as authenticated context, matching Shopify's actual webhook signing scheme guarantees.

### Proof of Concept
1. Install the target app on an attacker-controlled shop `attacker.myshopify.com`; trigger any webhook (e.g. `orders/create`) and capture the raw POST body `B` and the `x-shopify-hmac-sha256` header value `H` Shopify sends (valid because Shopify signs `B` with the app's shared `api_secret_key`).
2. Send a new POST to the app's webhook endpoint with:
   - body = `B` (unchanged)
   - `x-shopify-hmac-sha256: H` (unchanged)
   - `x-shopify-shop-domain: victim-shop.myshopify.com` (forged)
   - `x-shopify-topic` optionally forged as desired
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: forged_headers)` is constructed; `Utils::HmacValidator.validate` succeeds because it only checks `Digest.hexencode(...)` of `B` against `H`.
4. `ShopifyAPI::Webhooks::Registry.process` invokes the registered handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)`, causing the host app to act as though the (attacker-controlled) payload originated from the victim shop.

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

**File:** test/webhooks/registry_test.rb (L16-33)
```ruby
        hmac = OpenSSL::HMAC.digest(
          OpenSSL::Digest.new("sha256"),
          ShopifyAPI::Context.api_secret_key,
          "{}",
        )

        @headers = {
          "x-shopify-topic" => @topic,
          "x-shopify-hmac-sha256" => Base64.encode64(hmac),
          "x-shopify-shop-domain" => @shop,
          "x-shopify-webhook-id" => "b1234-eefd-4c9e-9520-049845a02082",
          "x-shopify-api-version" => "2024-01",
        }

        @webhook_request = ShopifyAPI::Webhooks::Request.new(raw_body: "{}", headers: @headers)
        @session = ShopifyAPI::Auth::Session.new(shop: ShopifyAPI::Context.host_name, access_token: "access_token")
        @url = "#{ShopifyAPI::Context.host}/admin/api/#{ShopifyAPI::Context.api_version}/graphql.json"
      end
```
