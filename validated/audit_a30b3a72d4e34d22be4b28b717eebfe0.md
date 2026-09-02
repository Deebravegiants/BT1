This confirms the vulnerability. The HMAC in `Webhooks::Request` covers only `@raw_body` via `to_signable_string` [1](#0-0) , while `topic`, `shop`, `api_version`, and `webhook_id` are all read directly from unauthenticated HTTP headers [2](#0-1) . `Registry.process` validates only the HMAC of the body and then forwards `request.shop` (the unauthenticated header) as the tenant identifier to the app's handler [3](#0-2) .

### Title
Webhook HMAC validation covers only the request body, not the `shop-domain` header, allowing cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body [1](#0-0) , and `Utils::HmacValidator.validate` computes/verifies the HMAC against that signable string only [4](#0-3) . The `shop` value passed downstream as the tenant identifier is read straight from the `shop-domain` header, which is never part of the signed bytes [5](#0-4) .

### Finding Description
The identity binding that should hold is:
`shop authenticated by HMAC == shop used as the tenant key for handler dispatch`

In `Registry.process`, this binding is broken:
```
raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
...
handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...))
``` [3](#0-2) 

`Utils::HmacValidator.validate` only checks `verifiable_query.to_signable_string` against the HMAC [6](#0-5) , and for webhooks that signable string is exactly `@raw_body` — nothing else [7](#0-6) . Meanwhile `shop`, `topic`, `api_version`, and `webhook_id` are all pulled unauthenticated from HTTP headers via `shopify_header` [8](#0-7) [9](#0-8) .

Before the attack: a legitimate webhook from Shopify for Shop A has `(body_A, hmac(body_A), shop-domain: A)`. After the attacker's request sequence: the attacker (who legitimately controls Shop A, e.g., a free/dev store where the same app is installed) receives this genuine, correctly-signed webhook delivery. Because the HMAC signs only `body_A`, the pair `(body_A, hmac(body_A))` remains valid for *any* header values. The attacker replays `(body_A, hmac(body_A))` to the app's public webhook endpoint but swaps the `x-shopify-shop-domain` header to Shop B (a victim tenant they do not control). `Utils::HmacValidator.validate` still returns `true` because it only recomputes the HMAC over `@raw_body`, and `Registry.process` then dispatches `WebhookMetadata` claiming `shop: "B"` with attacker-controlled body content, having already passed HMAC verification [3](#0-2) .

This is precisely the pattern of "a shop authenticated versus the shop stored as a session/tenant key" that this analysis targets: the gem's own HMAC check gives the host application false assurance that the entire webhook — including which shop it belongs to — is Shopify-authenticated, when in fact only the body bytes are.

### Impact Explanation
Any application that follows this gem's documented `Registry.process` flow and trusts `WebhookMetadata#shop` (the field this library explicitly exposes for tenant attribution) as an authenticated value will process attacker-supplied data under the identity of a victim shop it does not control. This is a cross-tenant integrity violation: attacker-controlled body content can be attributed to and processed against a different merchant's per-shop state (e.g., triggering shop-scoped side effects, poisoning shop-keyed caches/records, or invoking mandatory-topic handlers like `shop/redact` against the wrong shop) purely through HTTP header manipulation, with no credentials beyond running any Shopify store where the app is installed.

### Likelihood Explanation
The attacker only needs to install the target app on a store they legitimately control (which yields genuine HMAC-signed webhook deliveries for that store) and then replay the body+HMAC pair to the app's public webhook endpoint with a forged `shop-domain` header. No `api_secret_key`, access token, or privileged access is required — only the ability to send arbitrary HTTP requests, which any unprivileged internet user can do to a public webhook endpoint.

### Recommendation
Include the shop-identifying header (and ideally topic/webhook-id) in the HMAC-signed material, or otherwise cryptographically bind `shop` to the verified body before it is exposed via `WebhookMetadata`, so that `Registry.process` cannot dispatch a body verified for one shop under a different shop's identity. At minimum, `to_signable_string` in `lib/shopify_api/webhooks/request.rb` should incorporate the `shop-domain` header, and `HmacValidator` should fail closed if the header used downstream is not part of the signed payload.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker-shop.myshopify.com` and triggers a webhook (e.g., `orders/create`) with a chosen order payload `body_A`.
2. Shopify delivers `POST /webhooks` with headers `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-hmac-sha256: <hmac(body_A)>`, body `body_A`.
3. Attacker captures this exact request and resends it directly to the app's public webhook endpoint, changing only `x-shopify-shop-domain` to `victim-shop.myshopify.com`; `x-shopify-hmac-sha256` and the body are left untouched.
4. `Utils::HmacValidator.validate` recomputes the HMAC over `@raw_body` only [7](#0-6)  and it matches, so `Registry.process` proceeds and calls the registered handler with `shop: "victim-shop.myshopify.com"` and the attacker's `body_A` [10](#0-9) , causing the app to act on victim-shop's behalf using attacker-supplied data it never actually sent.

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

**File:** lib/shopify_api/webhooks/request.rb (L67-70)
```ruby
      sig { params(name: String).returns(T.untyped) }
      def shopify_header(name)
        @headers["shopify-#{name}"] || @headers["x-shopify-#{name}"]
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
