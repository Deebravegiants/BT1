### Title
Webhook `shop` (and `topic`/`webhook_id`/`api_version`) identity is read from unauthenticated headers while the HMAC only covers the raw body - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery` but its `to_signable_string` returns only `@raw_body` [1](#0-0) . The `shop`, `topic`, `webhook_id`, and `api_version` values that the registry uses to route and attribute the webhook are all read straight from HTTP headers, not from the signed payload [2](#0-1) . `HmacValidator.validate` only checks the HMAC against `to_signable_string` (the body), so it never binds `shop` to the signature [3](#0-2) . `Registry#process` then dispatches using the unverified `request.shop` value: `handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...))` [4](#0-3) .

### Finding Description
The bug class from the report is: `abi.encodePacked` mixes several dynamic values into one hash input, so the "signed" value can be satisfied by inputs that were never actually signed together — breaking the binding between the signature and the fields it's supposed to cover. The identity-binding analog here is structurally similar but simpler: the HMAC signature is computed over only one field (`raw_body`), while a security-relevant field (`shop`) that is *not* covered by that signature is nonetheless trusted and acted upon.

Concretely:
- `Request#hmac` is derived from the `X-Shopify-Hmac-Sha256` header [5](#0-4) .
- `Request#shop` is derived from the `X-Shopify-Shop-Domain` header [6](#0-5) .
- `Request#to_signable_string` (the value actually HMAC'd) is `@raw_body` only [1](#0-0) .
- The equality the gem is supposed to enforce is: `hmac_header == HMAC(secret, signed_fields)` where `signed_fields` should include `shop` (the tenant identity). Instead the actual equality enforced is `hmac_header == HMAC(secret, raw_body)`, i.e. `shop ⊄ signed_fields`.

Because `shop` sits outside the signed scope, any request satisfying `Request` initialization (i.e., presenting the three required headers plus a body) that carries a **valid `(raw_body, hmac)` pair for shop A** can have its `X-Shopify-Shop-Domain` header rewritten to shop B, and `Utils::HmacValidator.validate(request)` will still return `true`, because it only re-computes the HMAC over `raw_body` [7](#0-6) . The registry's `process` method then raises no error and hands the app's handler a `WebhookMetadata` whose `shop` says "B" while the actually-signed `body` content belongs to "A" [4](#0-3) .

### Impact Explanation
This breaks the tenant-identity binding the `signedOnly`-style HMAC check is supposed to guarantee: an app that keys any per-shop side effect (data storage, cache key, session lookup, uninstall/GDPR handling, billing update, etc.) off `WebhookMetadata#shop` inside its handler will attribute shop A's signed webhook payload to shop B. This is a cross-tenant data-confusion vector consistent with the "cross-tenant access" Critical-impact category, since the merchant-facing effect of a webhook meant for one shop is applied under a different shop's identity, all without possessing shop B's credentials.

### Likelihood Explanation
Exploitability requires the attacker to already be in possession of one valid `(raw_body, hmac)` pair — which any merchant who has installed the app can trivially obtain by triggering an ordinary webhook for their own shop (e.g. `orders/create`) and capturing the request Shopify sends to their app's public webhook endpoint. The webhook endpoint is a public, unauthenticated HTTP endpoint by design (Shopify calls it directly), so replaying the captured body/hmac with a swapped `X-Shopify-Shop-Domain` header is a low-effort, purely network-level attack requiring no secrets, no privileged account, and no TLS interception. Likelihood is High for apps that trust `WebhookMetadata#shop` for tenant-scoped side effects, which is the documented/intended use of that field.

### Recommendation
Bind `shop` (and ideally `topic`/`webhook_id`/`api_version`) into the value that is HMAC-verified, or otherwise cryptographically tie the header-derived shop to the signed body (e.g., require the shop domain to appear inside the signed payload/body and validate it there, rather than trusting a sibling header). At minimum, `Request#to_signable_string` should not diverge from the identity fields the registry uses in `process`; the safest fix mirrors the referenced fix pattern of moving to a canonical, unambiguous signed representation that includes every field that is subsequently trusted for authorization/routing decisions.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and triggers a webhook (e.g. updates an order) so Shopify sends a legitimately signed POST to the app's webhook endpoint, containing headers `X-Shopify-Hmac-Sha256: <hmac>`, `X-Shopify-Shop-Domain: attacker.myshopify.com`, `X-Shopify-Topic: orders/update`, and body `B`.
2. Attacker captures this full request (`hmac`, `B`).
3. Attacker replays the exact same body `B` and `hmac` header to the same endpoint, but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
4. `Utils::HmacValidator.validate(request)` recomputes `HMAC(secret, B)` and compares to the presented `hmac` — it matches, since `to_signable_string` never includes the shop header [1](#0-0) [8](#0-7) .
5. `Registry#process` proceeds and calls the app's handler with `WebhookMetadata.new(shop: "victim.myshopify.com", body: <attacker's order data>, ...)` [4](#0-3) , causing the app to process attacker-controlled webhook content as though it belongs to the victim shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
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
