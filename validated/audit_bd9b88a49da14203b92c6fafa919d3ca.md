### Title
Webhook shop-domain identity not covered by HMAC, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
The gem's webhook signature verification signs only the raw HTTP body, while the `shop` (tenant) identity used downstream by the host application's webhook handler is read from an unauthenticated header. This breaks the binding "shop authenticated == shop acted upon."

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop` accessor is derived purely from the `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header, which is never part of the signed content: [2](#0-1) 

`ShopifyAPI::Webhooks::Registry.process` validates the request solely via `Utils::HmacValidator.validate(request)`, which calls `to_signable_string` (i.e., verifies only the body bytes), and then immediately forwards `request.shop` — the unverified header value — as the tenant identity to the app's webhook handler: [3](#0-2) 

`Utils::HmacValidator.validate_signature` computes the HMAC over `verifiable_query.to_signable_string` (the body only) and compares it against the `hmac` header: [4](#0-3) 

Because the `api_secret_key` is a single per-app secret shared across every shop that installs the app (not a per-shop secret), any entity that can obtain one valid `(raw_body, hmac)` pair — e.g., by installing the app on their own shop and receiving one of their own legitimate webhooks — can replay that exact body and HMAC to the app's webhook endpoint while substituting an arbitrary value in the `shopify-shop-domain` header. `HmacValidator.validate` will still return `true` because the signature only covers the body, and `Registry.process` will hand the handler a `WebhookMetadata` (or equivalent, see `lib/shopify_api/webhooks/webhook_handler.rb`) whose `shop` field is the attacker-chosen domain rather than the domain that actually sent/owns that payload.

This is precisely the identity-binding class called out in scope: "a field acted on but not covered by the HMAC" and "a shop authenticated versus the shop stored as a session key" — here, the shop used by the host application to key sessions/data is not the shop verified by the signature.

### Impact Explanation
A host application built on this gem typically uses `WebhookMetadata#shop`/`data.shop` to look up the correct merchant session, scope data writes, or fan out to per-tenant storage. Since that shop value is unauthenticated, an attacker holding one valid signed webhook payload (trivially obtainable by installing the app on their own store) can cause the handler to process/attribute that data under a different, victim shop's tenant context — a cross-tenant data-integrity issue. This satisfies the "cross-tenant access" criterion in scope, since the confusion happens purely through the app-facing surface of this gem without needing the victim's access token or secret.

### Likelihood Explanation
Exploitation requires only: (1) becoming an app user (any merchant can install a public app), which yields one valid `(body, hmac)` pair signed with the shared `api_secret_key`; and (2) sending an HTTP POST to the app's public webhook endpoint with the captured body/hmac headers unchanged but the `shop-domain` header replaced with a victim shop's domain. No secrets, tokens, or elevated privileges beyond normal app installation are required, so the barrier to exploitation is low for anyone who is an unprivileged existing user of the app.

### Recommendation
Include the shop-domain (and ideally topic/webhook-id) in the value that is HMAC-verified, or otherwise cryptographically bind them to the signed body, so that `Utils::HmacValidator.validate` fails if any of these identity-bearing headers are altered relative to what Shopify actually signed. At minimum, `Webhooks::Request#to_signable_string` should not be limited to `@raw_body` alone when other unauthenticated fields are subsequently trusted as tenant identifiers by `Registry.process`/`WebhookHandler`.

### Proof of Concept
1. Install the target app on an attacker-controlled shop `attacker.myshopify.com`; capture a legitimate webhook: body `B`, header `x-shopify-hmac-sha256: H`, `x-shopify-shop-domain: attacker.myshopify.com`.
2. Replay a POST to the app's webhook endpoint with the same body `B` and same `hmac` header `H`, but set `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which computes the HMAC over `request.to_signable_string` (`= B`) and matches `H` — validation succeeds [5](#0-4) .
4. The handler receives `shop: "victim.myshopify.com"` [6](#0-5)  even though the payload actually originated from, and was signed for, the attacker's own shop.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
