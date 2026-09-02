### Title
Webhook HMAC verification signs only the raw body, letting an unprivileged caller reassign a legitimately-signed payload to any shop via the unauthenticated `shop-domain` header - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` implements `VerifiableQuery#to_signable_string` by returning only `@raw_body`, while the tenant identity (`shop`) is read from the `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header, which is never part of the signed bytes. `Utils::HmacValidator.validate` only proves that the *body* bytes were produced by someone holding `Context.api_secret_key`; it proves nothing about which shop that body belongs to. Since `api_secret_key` is one value shared across every shop that installs the app, any shop owner can capture a genuinely-signed webhook delivered to their own installation and replay the identical body to the app's public webhook endpoint with a forged `shop-domain` header pointing at a victim shop. `Registry.process` will pass HMAC validation and dispatch the payload to the handler tagged with the attacker-chosen shop.

### Finding Description
- `to_signable_string` (bytes verified) = `@raw_body` only: [1](#0-0) 
- `shop` (bytes acted on / tenant key) is taken straight from an HTTP header that is not part of the signed string: [2](#0-1) 
- `HmacValidator.validate` recomputes the HMAC over `to_signable_string` and only compares that against the received `hmac`; it never touches `shop`, `topic`, or `webhook_id`: [3](#0-2) 
- `Registry.process` validates the HMAC, then immediately trusts `request.shop` as the tenant for the handler call: [4](#0-3) 

The equality that should hold is: `shop value cryptographically bound inside the HMAC-covered signable string == shop value used to route/attribute the webhook`. Here it is instead: `shop value covered by HMAC = ∅` while `shop value used for routing = attacker-controlled header`, i.e. the binding is completely absent — this is exactly the "field acted on but not covered by the HMAC" pattern.

### Impact Explanation
Because `api_secret_key` is shared across all shops installing the same app, an attacker who installs the app on their own (attacker-controlled) shop can obtain a validly-HMAC-signed body from their own legitimate webhook deliveries, then resend that exact body to the app's public webhook endpoint while substituting a victim shop's domain in the header. The signature check still passes (it only checks body bytes), so the host application processes the event as if it came from the victim tenant. Depending on which webhook topic is abused (e.g. `app/uninstalled`, `shop/redact`, `customers/data_request`), this can be used to make the host app take destructive or data-disclosing actions against a victim tenant it never actually received a webhook from — a cross-tenant integrity/isolation break attributable directly to this gem's verification primitive.

### Likelihood Explanation
Exploitation requires only: (1) the ability to install the target app on an attacker-controlled development/trial shop (unprivileged, self-service), and (2) network access to the app's public webhook endpoint. No access token, `client_secret`, or privileged account is required — only ordinary internet access and use of the same shared secret's normal HMAC output obtained from the attacker's own legitimate traffic. This is squarely inside the "unprivileged internet user" threat model this scan targets.

### Recommendation
Bind the tenant identity into the material that is actually verified. Either (a) include `shop-domain`, `topic`, and `webhook-id` in `to_signable_string` so they are cryptographically covered by the same HMAC as the body, or (b) require callers of `Registry.process` to supply/verify the expected `shop` out-of-band (e.g. against a known list of installed shops) before trusting `request.shop`, rather than deriving tenant routing solely from an unauthenticated header.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker.myshopify.com` (self-service, no privilege needed).
2. Attacker triggers any subscribed webhook topic in their own shop; Shopify delivers a request to the app's webhook endpoint with headers including `X-Shopify-Hmac-Sha256: <hmac over raw body>` and `X-Shopify-Shop-Domain: attacker.myshopify.com`, and some `raw_body`.
3. Attacker captures this `raw_body` + `hmac` pair and resends it directly to the same public webhook endpoint, changing only `X-Shopify-Shop-Domain` to `victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` builds a request whose `hmac` still matches (`to_signable_string` is unchanged raw body): [5](#0-4) 
5. `ShopifyAPI::Webhooks::Registry.process(request)` calls `Utils::HmacValidator.validate(request)` → returns `true`, then dispatches `handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, ...))` with `shop == "victim.myshopify.com"`: [6](#0-5) 
6. The host application's handler executes tenant-scoped logic (e.g. deleting stored session/access token for the victim shop on `app/uninstalled`, or emitting a GDPR data payload) believing it originated legitimately from `victim.myshopify.com`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-23)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

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
