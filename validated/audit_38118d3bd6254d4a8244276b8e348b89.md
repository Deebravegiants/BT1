### Title
Webhook `shop-domain` header is not covered by HMAC verification, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the `shop` attribute (used to attribute an inbound webhook to a merchant/tenant) from the `X-Shopify-Shop-Domain` HTTP header, while the HMAC signature validated by `ShopifyAPI::Utils::HmacValidator` only covers the raw request body. This breaks the identity binding: `shop == HMAC-authenticated shop` is never actually enforced — the value handed to the host application's webhook handler is attacker-controllable while the signature stays valid.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

`shop` is read straight from the unauthenticated header, independent of the signed content: [2](#0-1) 

`ShopifyAPI::Utils::HmacValidator.validate` computes the HMAC exclusively over `verifiable_query.to_signable_string` (i.e., the raw body) and compares it against `Context.api_secret_key`/`old_api_secret_key`-derived digests — the `shop-domain` header plays no role in the signature: [3](#0-2) 

`ShopifyAPI::Webhooks::Registry.process` validates the HMAC and then immediately forwards the *unauthenticated* `request.shop` value to the app's handler as the tenant identifier, without any additional cross-check between the shop the HMAC actually authenticates and the shop attributed to the event: [4](#0-3) 

Because the same app's `api_secret_key` is shared across all of its installed shops, any unprivileged user who has installed the app on their own store (or otherwise obtained a legitimately-signed webhook body from Shopify) can capture a valid `(raw_body, hmac)` pair and replay it to the app's webhook endpoint while substituting an arbitrary `X-Shopify-Shop-Domain` header pointing at a victim shop. `HmacValidator.validate` still returns `true` because it never inspects the header, and the handler receives `WebhookMetadata` with `shop:` set to the attacker-chosen victim domain.

The equality that should hold but does not: `shop_authenticated_by_hmac == shop_used_by_handler`. In reality, `shop_used_by_handler` is taken from an out-of-band header the HMAC never covers, so the two can diverge completely.

### Impact Explanation
This is a cross-tenant identity confusion vulnerability at the core of the gem's webhook-processing primitive (`ShopifyAPI::Webhooks::Registry.process` / `ShopifyAPI::Webhooks::Request`, the gem's own documented API for consuming webhooks — see `docs/usage/webhooks.md`). Any host application that uses `data.shop` from `WebhookMetadata` to key into per-tenant data (the intended and documented usage pattern) can be tricked into writing/reading/acting on data under a victim shop's identity using a payload/signature the attacker legitimately obtained for their own shop. This satisfies the "cross-tenant access" Critical impact category, since the attacker crosses a tenant boundary using only their own legitimately-issued webhook material — no access token, `client_secret`, or privileged account is required.

### Likelihood Explanation
Likelihood is high for any unprivileged internet user who can install the target app (a standard, low-barrier action for a public Shopify app) or otherwise capture one legitimately signed webhook delivery. From there, forging the `X-Shopify-Shop-Domain` header on a replayed POST request is trivial and requires no cryptographic material beyond what Shopify already sent them.

### Recommendation
Bind the `shop-domain` (and ideally `topic`, `webhook-id`, `api-version`) header values into the signable string used for HMAC verification, or otherwise cryptographically bind the header set to the signature (e.g., by including the full canonicalized header+body as Shopify itself does not sign headers, so at minimum require the app to treat `X-Shopify-Shop-Domain` as authenticated data only after independently correlating the webhook to a known, previously-authorized shop/session, and reject any webhook whose asserted shop was never granted the app via OAuth/token exchange).

### Proof of Concept
1. Attacker installs the target app on `attacker.myshopify.com`, obtaining a legitimately Shopify-signed webhook delivery: `raw_body = '{"id":123}'` with header `X-Shopify-Hmac-Sha256: <valid HMAC over raw_body using the app's api_secret_key>` and `X-Shopify-Shop-Domain: attacker.myshopify.com`.
2. Attacker replays the exact same `raw_body` and `X-Shopify-Hmac-Sha256` value to the app's webhook endpoint, but changes the header to `X-Shopify-Shop-Domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` parses `shop` as `"victim.myshopify.com"`.
4. `ShopifyAPI::Utils::HmacValidator.validate(request)` recomputes the HMAC over `raw_body` only and finds it matches — validation succeeds: [5](#0-4) 
5. `Registry.process` invokes the handler with `WebhookMetadata(shop: "victim.myshopify.com", ...)`, and any host logic keyed on `data.shop` now operates against the victim tenant using attacker-supplied event data.

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
