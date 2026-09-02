This confirms the vulnerability: the webhook `shop` header is not covered by the HMAC signature, which only signs the raw body, exactly matching the identity-binding-break pattern the prompt targets.### Title
Cross-tenant webhook impersonation via unauthenticated `shop-domain` header — ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw request body only, while the tenant identifier (`shop`), along with `topic`, `webhook_id`, and `api_version`, is read directly from unauthenticated HTTP headers. `ShopifyAPI::Webhooks::Registry.process` validates the HMAC and then hands the unauthenticated `shop` value straight to the app's webhook handler as the trusted tenant identity. The binding that should hold — "the shop the HMAC authenticates" == "the shop the handler acts on" — is broken.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop`, `#topic`, `#webhook_id`, and `#api_version` are all pulled from HTTP headers that are never included in that signable string: [2](#0-1) 

`HmacValidator.validate` only checks `computed_signature(verifiable_query.to_signable_string)` against the received HMAC — i.e., it authenticates the raw body bytes only: [3](#0-2) 

`Registry.process` calls this HMAC check and then immediately forwards `request.shop` (an unauthenticated header value) into `WebhookMetadata`, which the host app's handler treats as the authoritative tenant for the payload: [4](#0-3) 

The gem's own test suite demonstrates that the `shop` field is entirely separate from what the HMAC covers — the HMAC is computed only over the JSON body (`"{}"`), while `shop` is set independently via a header: [5](#0-4) 

Because the HMAC secret (`Context.api_secret_key`) is a single **per-app** secret shared across every shop that installs the app, any unprivileged actor who can install the app on their own store (or otherwise obtain one valid `(raw_body, hmac)` pair generated for their own tenant) possesses a signature that is valid for that exact body regardless of which `shop-domain` header accompanies it. The identity equality this design is meant to preserve is:

`shop asserted by HMAC-covered content == shop consumed by Registry.process/WebhookMetadata`

but since the HMAC covers only `raw_body` and never `shop`, the attacker can freely vary the `shop-domain` header on a replayed body while the signature check still passes.

### Impact Explanation
This breaks the cross-tenant boundary the library is expected to enforce for webhook delivery: an attacker who legitimately owns one shop under the app can capture a `(raw_body, x-shopify-hmac-sha256)` pair from their own webhook deliveries and resend it to the app's webhook endpoint with the `X-Shopify-Shop-Domain` (or `Shopify-Shop-Domain`) header changed to any victim shop domain. `HmacValidator.validate` still returns `true` because it only checks the body bytes, and `Registry.process` passes the attacker-chosen `shop` straight into the handler's `WebhookMetadata`. Any app logic that uses `data.shop` to select which merchant's records to update, credit, or delete (a standard pattern shown in the gem's own webhook documentation) can be tricked into attributing/processing data under a shop the attacker does not control — i.e., cross-tenant data injection/corruption using only the attacker's own legitimate app install, no `client_secret`, access token, or TLS interception required.

### Likelihood Explanation
High. The prerequisite is only an ordinary, unprivileged Shopify store that installs the target app (a normal, self-serve action), plus the ability to send an HTTP POST to the app's public webhook endpoint with attacker-controlled headers — both trivially available to any internet user. No credential leakage, TLS interception, or privileged account is required; the attacker only needs one authentic webhook delivery of their own to harvest a valid `(body, hmac)` pair.

### Recommendation
Bind the identity fields into the signed content, or otherwise cryptographically tie `shop`, `topic`, `webhook_id`, and `api_version` to the verified payload before they are trusted by `Registry.process`/`WebhookMetadata`. At minimum, the library should require callers to cross-check `request.shop` against a set of shops known to have valid, gem-issued OAuth sessions/access tokens before treating the header as authoritative, and should document prominently that `shop-domain` (and the other Shopify-* headers) are **not** covered by the HMAC and must not be trusted as tenant identity on their own.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker-shop.myshopify.com` and triggers a webhook subscription (e.g. `orders/create`).
2. Shopify delivers a webhook to the app with headers `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`, `X-Shopify-Hmac-Sha256: <valid hmac of raw_body>`, and some `raw_body`.
3. Attacker captures the exact `raw_body` and `X-Shopify-Hmac-Sha256` value from step 2.
4. Attacker sends a new POST to the app's webhook endpoint with the identical `raw_body` and `X-Shopify-Hmac-Sha256` header, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
5. `ShopifyAPI::Webhooks::Request.new` parses this request; `HmacValidator.validate` recomputes the HMAC over `raw_body` only (per `to_signable_string`) and it matches, so the request is treated as authentic. [6](#0-5) 
6. `Registry.process` dispatches to the app handler with `WebhookMetadata#shop == "victim-shop.myshopify.com"`, even though the body actually originated from the attacker's own shop. [7](#0-6)

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

**File:** test/webhooks/registry_test.rb (L14-30)
```ruby
        @shop = "shop.myshopify.com"

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
