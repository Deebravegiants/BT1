### Title
Webhook `shop-domain`/`topic`/`webhook-id` headers are trusted by the host app but excluded from the HMAC signature, allowing cross-tenant webhook forgery via replay - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body, while `WebhookHandler`/`WebhookMetadata` consumers act on the `shop`, `topic`, `webhook_id`, and `api_version` values that are parsed from HTTP headers and never covered by the HMAC. This is the same class of bug as the C4 report's "double entry token" issue: the code validates one representation of the data (`hmac` over `raw_body`) but acts on another representation (`shop`/`topic` headers) that is not bound to that validated signature.

### Finding Description
`Utils::HmacValidator.validate` accepts any object implementing `VerifiableQuery` and checks `OpenSSL.secure_compare(computed_signature, hmac)` where `computed_signature = HMAC(secret, verifiable_query.to_signable_string)`: [1](#0-0) 

For webhooks, `to_signable_string` is defined as just the raw body: [2](#0-1) 

But `Registry.process` uses `request.shop`, `request.topic`, and `request.webhook_id` — all parsed from HTTP headers, not from the signed body — to build the `WebhookMetadata` object dispatched to the app's handler: [3](#0-2) 

`Request#shop`, `#topic`, and `#webhook_id` are all sourced from `shopify_header`, which reads directly from the (attacker-controllable, in a replay scenario) `headers` hash passed into `Request.new`: [4](#0-3) [5](#0-4) 

The identity binding that should hold is: `hmac == HMAC(secret, shop || topic || webhook_id || body)`, i.e., every field the app acts on for tenant/topic identification must be cryptographically bound to the signature. Instead the binding actually implemented is `hmac == HMAC(secret, body)` only — `shop`, `topic`, and `webhook_id` are outside the signed content, exactly analogous to the C4 finding where the code validated "is this address a duplicate in the array" but not "does this address correspond to a distinct real balance," allowing the unchecked dimension (secondary token address / here, header values) to be manipulated independently of the checked dimension (array de-dup / here, HMAC).

### Impact Explanation
Any party who can observe (or is the origin merchant of) one legitimate webhook delivery — body + valid HMAC for that body — can replay the exact same body/HMAC pair to the app's webhook endpoint while substituting a different `shop-domain`, `topic`, or `webhook-id` header. `Utils::HmacValidator.validate` will still succeed (it only checks the body), and `Registry.process` will dispatch a `WebhookMetadata` claiming the forged `shop`/`topic`/`webhook_id` to the host app's handler: [6](#0-5) 

Since host applications are expected (per this gem's documented contract, `WebhookMetadata#shop`) to trust `data.shop` as the tenant identity for storing/updating per-shop state, this breaks the shop-identity binding and enables cross-tenant data confusion/injection — e.g., an app that keys webhook-driven writes (order sync, uninstall handling, GDPR data, etc.) by `data.shop` could have another merchant's legitimate webhook body attributed to a victim shop, or a shop's own webhook falsely attributed to a different topic.

### Likelihood Explanation
This requires the attacker to already possess one valid body+HMAC pair for their own store's webhook (achievable trivially since any merchant receives webhooks for their own shop) and the ability to POST directly to the app's public webhook endpoint with custom headers — no `api_secret_key`, access token, or privileged account needed. This is a realistic unprivileged-internet-user attack path, though its severity depends on how the host application uses `WebhookMetadata#shop`/`#topic` (the gem's own responsibility ends at handing the app this unverified header data as if verified).

### Recommendation
Include `shop`, `topic`, and `webhook_id` in the signable string used for HMAC verification (or otherwise cryptographically bind the header-derived identity fields to the signed payload), so `to_signable_string` in `lib/shopify_api/webhooks/request.rb` reflects everything the app subsequently trusts, matching how `Auth::Oauth::AuthQuery#to_signable_string` already includes `shop` in its signed fields.

### Proof of Concept
1. Merchant A's shop receives a legitimate webhook: `POST /webhooks` with `X-Shopify-Shop-Domain: shop-a.myshopify.com`, `X-Shopify-Topic: orders/create`, raw body `B`, and `X-Shopify-Hmac-Sha256: HMAC(secret, B)`.
2. Attacker (who is shop A's own merchant, or intercepts the request) resends the identical body `B` and HMAC header, but changes `X-Shopify-Shop-Domain` to `shop-b.myshopify.com` (a different, victim tenant) and/or changes `X-Shopify-Topic`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(secret, request.to_signable_string)` — equal to `HMAC(secret, B)` regardless of headers — so validation succeeds: [7](#0-6) 
4. The forged `shop`/`topic` values are passed straight into the app's handler via `WebhookMetadata`, which the host app trusts as the authenticated tenant/topic for this webhook delivery.

### Citations

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

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

**File:** lib/shopify_api/webhooks/request.rb (L45-70)
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

      private

      sig { params(name: String).returns(T.untyped) }
      def shopify_header(name)
        @headers["shopify-#{name}"] || @headers["x-shopify-#{name}"]
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
