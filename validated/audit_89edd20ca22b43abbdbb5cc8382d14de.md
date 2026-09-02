## Title
Webhook HMAC only authenticates the request body, not the `shop`/`topic` headers, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats a passing HMAC check as proof that an entire incoming webhook — including its `shop`, `topic`, `webhook_id`, and `api_version` — is authentic and safe to hand to the app's handler. In reality, the HMAC only ever covers the raw request body. An attacker who can obtain any single genuine `(body, hmac)` pair signed by the app's secret (trivially available by simply installing the app on a store they control) can replay that pair to the app's public webhook endpoint while freely rewriting the `shop-domain`, `topic`, `webhook-id`, and `api-version` headers. This breaks the identity binding `authenticated_shop == acted_upon_shop`, enabling one tenant to inject events that the host app will process as belonging to a different, victim tenant.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

but the same object exposes `shop`, `topic`, `webhook_id`, and `api_version` derived purely from unauthenticated HTTP headers, with no cross-check against the signed content: [2](#0-1) 

`Registry.process` validates only the HMAC over that signable string (the body), then unconditionally dispatches to the handler using the unauthenticated `topic` and forwards the unauthenticated `shop` straight into `WebhookMetadata` for the app's business logic to consume: [3](#0-2) 

Because the HMAC never binds `shop` (or `topic`) to the body, the equality the app implicitly relies on —
`hmac_verified(body) == hmac_verified(shop, topic, body)`
— does not hold. Anyone who has ever received one genuine webhook delivery from Shopify for the app (e.g. by simply installing the app on their own store and subscribing to any webhook topic) possesses a valid `(raw_body, hmac)` pair signed with the app's `api_secret_key`. They can POST that exact body/HMAC to the app's public webhook endpoint any number of times while substituting the `shopify-shop-domain` header with an arbitrary victim shop's domain and the `shopify-topic` header with any topic name registered by the app. `Utils::HmacValidator.validate` will succeed because it only recomputes the HMAC over `@raw_body`: [4](#0-3) 

The library provides no mechanism, and the docs describe none, for the app to additionally verify that the `shop`/`topic` headers correspond to the actual sender — the API surface (`Registry.process`) presents HMAC success as full request authentication.

### Impact Explanation
This allows cross-tenant data/event injection: a host app that trusts `WebhookMetadata#shop` (as the library's own `process` flow implies is safe once HMAC passes) will execute business logic — updating records, firing side effects, marking orders/fulfillments, revoking access, etc. — under an attacker-chosen victim shop's identity, and can dispatch attacker-chosen topics that were never actually sent for that shop. This is a cross-tenant identity-binding bypass driven entirely by this gem's `process`/`Request` design, matching the Critical "cross-tenant access" impact category.

### Likelihood Explanation
High. No privileged access, leaked secrets, or social engineering is required — only the ability to install the app for one's own store (the normal onboarding flow for any Shopify merchant) or otherwise capture one legitimate webhook body+HMAC, followed by a single unauthenticated HTTP POST to the app's public webhook route with forged headers.

### Recommendation
Include the security-relevant headers (`shop`, `topic`, `webhook_id`, `api_version`) in the HMAC-signable content, or otherwise cryptographically bind them (e.g., require the host app to independently verify `shop` against a known/allow-listed tenant before trusting `WebhookMetadata#shop`), and document explicitly in `Registry.process` that a passing HMAC only authenticates the body, not the headers, so integrators do not assume `shop`/`topic` are verified.

### Proof of Concept
1. Install the target app on an attacker-owned Shopify development store; trigger any webhook topic the app subscribes to and capture the raw body `B` and the `X-Shopify-Hmac-Sha256` value `H` that Shopify sent (valid because it's HMAC-SHA256(`B`, app's real `api_secret_key`)).
2. Send a request directly to the app's public webhook endpoint:
```
POST /webhooks HTTP/1.1
X-Shopify-Topic: orders/paid
X-Shopify-Hmac-Sha256: H
X-Shopify-Shop-Domain: victim-shop.myshopify.com
Content-Type: application/json

B
```
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {...})` is constructed with `shop == "victim-shop.myshopify.com"` and `topic == "orders/paid"`. [5](#0-4) 
4. `Registry.process` recomputes HMAC over `B` only, matches `H`, and dispatches the `orders/paid` handler with `WebhookMetadata#shop == "victim-shop.myshopify.com"` — despite the event never having originated from that shop. [3](#0-2)

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

**File:** lib/shopify_api/webhooks/request.rb (L45-60)
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
