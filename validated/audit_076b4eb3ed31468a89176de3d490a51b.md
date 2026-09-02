## Finding

The Chainlink bug class here is "a value is trusted for identity/authorization purposes while a different, unguarded value is the one that actually gets acted upon." In this gem's webhook processing path, that same class of bug is present: the shop identity handed to application logic is **not** covered by the HMAC signature that is supposed to authenticate the request.

### Root cause

`ShopifyAPI::Webhooks::Request#to_signable_string` returns **only the raw body** — it does not include the `shop-domain`, `topic`, `webhook-id`, or `api-version` headers: [1](#0-0) [2](#0-1) 

`HmacValidator.validate` computes the HMAC exclusively over `to_signable_string`: [3](#0-2) 

`Webhooks::Registry.process` validates that HMAC and then dispatches to the handler using `request.shop` (the unsigned header) as the tenant identity: [4](#0-3) 

So the equality that is supposed to hold is:

`shop authenticated by the HMAC == shop delivered to the application's handler (data.shop)`

But because `shop` (and `topic`/`webhook_id`) are excluded from the signed bytes, this equality is never actually checked — only the *body* is authenticated, while the *shop* attribution is taken on faith from an unsigned header. This is precisely analogous to `ChainlinkUtil::getPrice` trusting a value (`minAnswer`) that superficially looks validated but isn't actually checked against the real constraint.

### Exploit path (unprivileged internet user, no leaked credentials needed)

1. Attacker installs the target multi-tenant app on their own store (`attacker-shop.myshopify.com`) — a normal, unprivileged action any merchant can take.
2. Using their own (legitimately granted) access token for their own shop, the attacker registers/points a webhook subscription's callback address to a server they control.
3. Attacker triggers an event with body content of their choosing (e.g., `orders/create` with fabricated data). Shopify signs this body with the app's shared `api_secret_key` and delivers it to the attacker's server — giving the attacker a valid `(body, hmac)` pair for content they fully control.
4. Attacker replays that exact `body` + `X-Shopify-Hmac-Sha256` value to the app's real public webhook endpoint, but swaps `X-Shopify-Shop-Domain` to a victim shop's domain.
5. `HmacValidator.validate` still returns `true` (it only checks the body/hmac pair, which is valid), so `Registry.process` calls the handler with `shop: request.shop` set to the victim's domain and attacker-controlled body data.

This lets an attacker inject fabricated webhook events attributed to an arbitrary victim tenant, poisoning per-merchant state, triggering merchant-scoped side effects, or otherwise achieving cross-tenant data injection under a shop identity the attacker doesn't control — without ever needing `api_secret_key`, an access token belonging to the victim, or any other privileged material.

### Title
Webhook shop/topic identity is not covered by HMAC verification, enabling cross-tenant webhook spoofing — (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` signs only the raw body, excluding the `shop-domain`, `topic`, and `webhook-id` headers, while `Registry.process` trusts `request.shop`/`request.topic` for dispatch after HMAC validation passes.

### Finding Description
The HMAC in `HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:26-31`) authenticates only the byte sequence returned by `to_signable_string`, which for webhooks is just `@raw_body` (`lib/shopify_api/webhooks/request.rb:35-38`). The `shop` accessor pulls straight from the unsigned `x-shopify-shop-domain`/`shopify-shop-domain` header (`lib/shopify_api/webhooks/request.rb:20-23`). `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) checks the HMAC and then unconditionally forwards `request.shop` to the handler as the tenant identity. Because the header is outside the signed payload, any entity capable of producing one valid `(body, hmac)` pair for their own shop (trivially available to any merchant who installs the app) can present that same pair with a different `shop-domain` header value and have it accepted as coming from that other shop.

### Impact Explanation
This breaks the tenant isolation the HMAC is meant to enforce, letting an attacker deliver arbitrary attacker-authored webhook payloads under another merchant's shop identity. Depending on how the host application's webhook handlers consume `data.shop`/`data.body`, this can lead to cross-tenant data corruption, unauthorized state changes scoped to a victim's shop, or forged business events — a cross-tenant access impact.

### Likelihood Explanation
Requires only the ability to install the app on one's own shop and register/observe one legitimate webhook delivery (both are standard, unprivileged merchant actions), plus the ability to send an arbitrary HTTP POST to the app's public webhook endpoint (which is normally internet-reachable by design). No secrets, tokens, or privileged access belonging to the victim are needed.

### Recommendation
Include the identifying headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the signed material used for verification, or otherwise cryptographically bind them to the body before trusting `request.shop`/`request.topic` in `Registry.process`. At minimum, document and/or enforce that consuming applications must cross-check `request.shop` against an independently known/registered shop for the webhook subscription rather than trusting the header outright.

### Proof of Concept
1. Install the app on `attacker.myshopify.com`; register a webhook to attacker-controlled endpoint.
2. Trigger an event to capture a valid `(raw_body, X-Shopify-Hmac-Sha256)` pair.
3. POST that same body/HMAC to the app's production webhook endpoint with `X-Shopify-Shop-Domain: victim.myshopify.com`.
4. Observe `ShopifyAPI::Webhooks::Registry.process` accepts it (`Utils::HmacValidator.validate` returns `true`) and invokes the handler with `shop: "victim.myshopify.com"` and attacker-controlled body.

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
