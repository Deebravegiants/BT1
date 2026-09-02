This confirms the finding: the webhook HMAC in `to_signable_string` covers only `@raw_body`, while `shop` (from `x-shopify-shop-domain`/`shopify-shop-domain`) is read independently from headers, unauthenticated by the signature.Based on my investigation, I've confirmed the vulnerability. Here is the analog finding.

### Title
Webhook shop identity is not covered by the HMAC signature, allowing cross-tenant shop spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body [1](#0-0) , so the HMAC verification performed in `Utils::HmacValidator.validate` only proves the *body bytes* were signed by Shopify with the app's secret [2](#0-1) . The `shop` value used downstream for all business logic, however, is read directly from the `x-shopify-shop-domain`/`shopify-shop-domain` HTTP header, which is completely outside the signed content [3](#0-2) . `Registry.process` validates the HMAC and then immediately trusts `request.shop` to build the `WebhookMetadata` passed to the app's handler [4](#0-3) .

### Finding Description
The identity binding that should hold is: `shop authenticated by HMAC == shop used to route/process the webhook`. In this implementation that equality does not hold, because the HMAC only binds the body, not the shop header.

Any entity capable of triggering a genuine webhook delivery from Shopify for *any* shop that has installed the target app (e.g., an unprivileged merchant/attacker who installs the app themselves) receives an authentic `(raw_body, hmac)` pair signed with the app's shared secret. Because `topic`, `shop-domain`, `webhook-id`, and `api-version` are not part of `to_signable_string`, that captured, validly-signed `(raw_body, hmac)` pair can be replayed to the app's webhook endpoint with the `x-shopify-shop-domain` header swapped to any other (victim) shop domain, and `Utils::HmacValidator.validate` will still return `true` [5](#0-4) . `Registry.process` will then invoke the registered handler with `shop: request.shop` set to the attacker-chosen victim shop domain [6](#0-5) .

### Impact Explanation
This is a cross-tenant identity confusion: an unprivileged user of the app (one merchant/shop) can cause the host application's webhook handler to process forged/replayed event data attributed to a different merchant's shop namespace. Since most Shopify apps key their per-tenant data mutations directly off the webhook's `shop` field (e.g., "update orders for shop X", "update inventory for shop X"), this can lead to cross-tenant data corruption or cross-tenant data disclosure inside the host application, entirely from the perspective of an "unprivileged internet user" who only needs their own legitimate installation of the target app to obtain one valid signed payload.

### Likelihood Explanation
Any developer/customer who installs the target Shopify app receives real webhook deliveries signed with the app's `client_secret` for their own shop. Capturing one `(raw_body, x-shopify-hmac-sha256)` pair (via their own server logs, a reverse proxy, or simply their own webhook endpoint) requires no privilege beyond a normal app installation. Replaying it against the shared webhook endpoint with a modified `shop-domain` header is a straightforward HTTP request; there is no additional check anywhere in `Registry.process` or `Request` that ties the `shop` header to the signed body or to a known/expected shop.

### Recommendation
Include the `shop` (and ideally `topic`/`webhook_id`) values in the string that is HMAC-verified, or otherwise cryptographically bind them to the signed body before trusting `request.shop` in `Registry.process`. At minimum, document that host applications must independently verify `request.shop` against a shop they know installed the app (matching Shopify's own guidance), since the gem currently exposes `WebhookMetadata#shop` as if it were authenticated when it is not covered by `HmacValidator.validate`.

### Proof of Concept
1. Attacker installs the target Shopify app on their own shop `attacker.myshopify.com`, gets a real webhook delivery for topic `orders/create` with body `B` and header `x-shopify-hmac-sha256: H` (valid HMAC of `B` with the app's secret) — captured via attacker's own webhook receiver/logs.
2. Attacker sends `POST /webhooks` to the target app's endpoint with body `B`, header `x-shopify-hmac-sha256: H`, but `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses the forged headers [7](#0-6) ; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `B` against `H` [8](#0-7) .
4. The registered handler receives `WebhookMetadata.new(topic:, shop: "victim.myshopify.com", body:, ...)` and processes attacker-controlled order data as if it belonged to `victim.myshopify.com` [9](#0-8) .

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
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
