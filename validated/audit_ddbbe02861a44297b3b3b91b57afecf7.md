### Title
Webhook shop identity spoofing via shop-domain header not covered by HMAC — ([File: lib/shopify_api/webhooks/request.rb])

### Finding Description
`ShopifyAPI::Webhooks::Request` extracts the `shop` used for dispatching webhook handling directly from the `X-Shopify-Shop-Domain` (or `shopify-shop-domain`) HTTP header: [1](#0-0) 

But the value that is actually HMAC-verified is only the raw request body — the `shop` header is never included in the signable string: [2](#0-1) 

`Registry.process` validates the HMAC and then unconditionally trusts `request.shop` to build the `WebhookMetadata` that is handed to the app's webhook handler: [3](#0-2) 

`HmacValidator.validate` computes/verifies the signature purely over `to_signable_string` (the raw body), never over headers: [4](#0-3) 

This is the same bug class as the reported issue: a field that downstream code acts on (`shop`) is not covered by the integrity check (`hmac`), breaking the intended binding `hmac_verified_bytes == bytes_the_app_trusts_for(shop)`.

Shopify signs webhooks using the **app's `api_secret_key`, shared across every shop that installs the app** — not a per-shop secret. Therefore any merchant (including an attacker) who legitimately installs the app receives real webhook deliveries with a valid `X-Shopify-Hmac-Sha256` value computed over a body they fully control (they choose what data exists on their own shop, e.g. product/order content, and can trigger webhook delivery). Because the `shop` domain is excluded from the signed bytes, the attacker can capture one of these (body, hmac) pairs and replay it to the app's public webhook endpoint with the `X-Shopify-Shop-Domain` header rewritten to a victim shop's domain. `HmacValidator.validate` still returns `true` (the body/hmac pair is valid for the shared secret), and `Registry.process` dispatches the handler with `WebhookMetadata#shop` set to the attacker-chosen victim domain.

### Impact Explanation
This breaks the identity binding `authenticated_shop == shop_the_handler_processes_data_for`, enabling cross-tenant confusion: an attacker can make the app believe attacker-controlled webhook content (arbitrary body) originated from a different merchant's shop. Depending on how the host app implements handlers (e.g. mandatory compliance webhooks `customers/redact`, `shop/redact`, `customers/data_request`, or business-logic webhooks like `orders/create`), this can cause the app to perform actions, store data, or make privileged decisions against the wrong tenant using attacker-controlled content — a cross-tenant data integrity/confusion issue.

### Likelihood Explanation
Requires only an attacker-controlled Shopify shop (any developer/free/dev store can install a public app) and knowledge of the app's webhook endpoint — no access to the `api_secret_key`, access tokens, or victim credentials is needed. The library provides no built-in binding of the shop header to the signature, so any host app relying solely on `ShopifyAPI::Webhooks::Registry.process` for authentication is exposed.

### Recommendation
Do not treat the `shop` header as authenticated by `HmacValidator.validate`. Either:
1. Include the shop domain (and other headers this claim/processing depends on) in the HMAC-signed payload used for verification, or
2. Require callers of `Registry.process`/`WebhookMetadata` to additionally verify `request.shop` against the set of shops that have valid installations/access tokens for the app (e.g., cross-check against stored session data) before trusting it, and document this requirement prominently, since the header itself carries no cryptographic guarantee.

### Proof of Concept
1. Attacker installs the target app on their own dev shop `attacker.myshopify.com`, obtaining genuine webhook deliveries signed with the app's shared `api_secret_key`.
2. Attacker triggers a webhook (e.g., by creating an order) and captures the raw body `B` and its valid `X-Shopify-Hmac-Sha256` value `H` (valid because `HmacValidator` only signs `B`).
3. Attacker sends a POST request to the app's webhook endpoint with body `B`, header `X-Shopify-Hmac-Sha256: H` unchanged, but `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `B`/`H` against the secret [5](#0-4) .
5. The handler is invoked with `WebhookMetadata.new(... shop: "victim-shop.myshopify.com", body: parsed(B) ...)`, so the app processes attacker-controlled data as if it belonged to the victim shop [6](#0-5) .

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

**File:** lib/shopify_api/webhooks/registry.rb (L188-199)
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
