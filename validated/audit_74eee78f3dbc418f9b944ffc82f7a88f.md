### Title
Webhook `shop-domain` header is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary

### Finding Description
Shopify webhook authenticity is verified by `ShopifyAPI::Utils::HmacValidator.validate`, which recomputes an HMAC over `verifiable_query.to_signable_string` and compares it to the `hmac-sha256` header using a constant-time comparison [1](#0-0) .

For incoming webhooks, `ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body — it does not include the `shop`, `topic`, `api_version`, or `webhook_id` values that are read from unauthenticated HTTP headers: [2](#0-1) 

`ShopifyAPI::Webhooks::Registry.process` validates the HMAC and then immediately trusts `request.shop` (and other header-derived fields) to build the `WebhookMetadata` passed to the app's handler, without any additional binding between the verified body and the asserted shop: [3](#0-2) 

Because the same `api_secret_key` is shared across every shop that installs the app, the equality the system needs to hold is:

`shop cryptographically bound by the HMAC == shop the handler treats as the webhook's tenant`

That equality does not hold here: the HMAC only authenticates *that the body came from Shopify using this app's secret*, not *which shop* that body belongs to. The `shop-domain` header is a field acted on (used as the tenant identifier for the handler) but not covered by the HMAC.

### Impact Explanation
An unprivileged user who can install the app on their own shop (a normal, legitimate tenant) can trigger a genuine webhook delivery for that shop and capture a valid `(raw_body, hmac)` pair signed with the app's shared secret. Because the signature covers only the body, that same `(raw_body, hmac)` pair remains valid for any `x-shopify-shop-domain` header value the attacker chooses to send in a replayed/forged request to the app's webhook endpoint. `Registry.process` will pass HMAC validation and dispatch the handler with an attacker-chosen `shop`, `webhook_id`, `api_version`, and `topic` value paired with a body that was actually generated for the attacker's own shop. If the host application's webhook handler uses the `shop` field from `WebhookMetadata` to select tenant context (session/store lookup, side effects, data writes) — which is the documented purpose of `WebhookMetadata#shop` — this allows cross-tenant confusion: the app can be made to believe order/customer/inventory data belongs to a victim shop while actually driven by attacker-controlled content, or to apply the wrong tenant's webhook body against another tenant's state.

### Likelihood Explanation
Exploitation only requires the capability any legitimate merchant already has: installing the app and receiving one real webhook for their own shop (no `api_secret_key`, access token, or other privileged material is required — the HMAC is intentionally computed by Shopify for a real event). The header replacement (`x-shopify-shop-domain`) is a trivial HTTP header edit against the app's public webhook endpoint. The binding gap is deterministic and always present, not a timing or race condition, so any host application that relies on `WebhookMetadata#shop` for tenant routing is exposed.

### Recommendation
Include the identifying headers (`shop-domain`, `topic`, `api_version`, `webhook_id`) in the HMAC-signed content, or otherwise cryptographically bind them, e.g. by having `Request#to_signable_string` return a canonical concatenation of the raw body plus the header values used downstream, so `HmacValidator.validate` fails if any of those fields are altered relative to what Shopify actually signed. At minimum, document prominently that `WebhookMetadata#shop`/`#topic`/etc. are not covered by the HMAC and must not be trusted as tenant identifiers without independent verification (e.g., cross-checking against a shop known to have an active, matching webhook subscription/session).

### Proof of Concept
1. Attacker installs the app for `attacker-shop.myshopify.com` and lets Shopify deliver a real webhook, e.g. `orders/create`, capturing:
   - `raw_body = B`
   - `x-shopify-hmac-sha256 = H` (valid HMAC of `B` with the app's `api_secret_key`)
2. Attacker sends a POST to the app's webhook endpoint with the same `raw_body = B` and `x-shopify-hmac-sha256 = H`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com` and any desired `x-shopify-topic`/`x-shopify-webhook-id`.
3. `ShopifyAPI::Webhooks::Request.new` parses these headers [4](#0-3) ; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `B` against `H` [5](#0-4) .
4. The handler is invoked with `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: parsed_body, ...)` [6](#0-5)  — the app processes attacker-controlled content under the victim shop's identity.

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L20-38)
```ruby
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
