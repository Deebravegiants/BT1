### Title
Webhook `shop` identity is trusted from an unauthenticated header while only the raw body is HMAC-covered, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body, so the HMAC signature validated by `Utils::HmacValidator` proves nothing about the `shop-domain` header. `Registry.process` nonetheless takes `request.shop` straight from that unauthenticated header and forwards it as the tenant identity to the app's `WebhookHandler`. This breaks the identity binding `HMAC(secret, body) == received_hmac` ⇏ `shop == authenticated_shop`.

### Finding Description
- `Request#to_signable_string` signs only `@raw_body`: [1](#0-0) 
- `Request#shop` is read verbatim from the `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header, which is never part of the signed content: [2](#0-1) 
- `Registry.process` validates only the body's HMAC and then dispatches to the handler using the unverified `request.shop`: [3](#0-2) 
- `HmacValidator.validate` computes/compares the signature purely over `to_signable_string` (i.e. body only), so headers such as `shop-domain`, `topic`, `webhook-id`, and `api-version` are all "bytes parsed but not bytes verified": [4](#0-3) 

Because Shopify signs webhooks with the app's single `client_secret` — the same secret used for every shop that has the app installed — any merchant who installs the app on their own store (an unprivileged internet user with respect to any other tenant) legitimately receives genuine `(body, hmac)` pairs signed with that shared secret. That attacker can then replay the exact same body/HMAC pair to the app's webhook endpoint while substituting the `shop-domain` header for a victim shop's domain. `Registry.process` still finds `Utils::HmacValidator.validate(request)` to be `true` (the body/HMAC pair is genuinely valid), and forwards `shop: <victim_domain>` to the handler, letting the attacker inject arbitrary webhook payloads (of whatever topic they can generate on their own shop, e.g. `orders/create`, `app/uninstalled`, `customers/data_request`) that the host application will process as if they originated from the victim's shop.

### Impact Explanation
This is a cross-tenant access vulnerability: it lets one shop's genuinely-signed webhook payload be attributed to a different, arbitrary shop merely by forging an HTTP header. Any app logic keyed off `WebhookMetadata#shop` (e.g. shop lookup, data sync, GDPR redaction routines, uninstall handling, billing state changes) can be triggered against a victim tenant using attacker-controlled body content. This matches the Critical "cross-tenant access" category.

### Likelihood Explanation
Any developer/merchant can install a public Shopify app for free, thereby obtaining a stream of genuinely HMAC-signed webhooks for their own shop. Forging the `shop-domain` header on a subsequent HTTP POST to the app's public webhook endpoint requires no secret knowledge and only knowledge of the victim's shop domain, which is typically public (`*.myshopify.com`). No credentials, tokens, or privileged access are required — likelihood is high for any app that keys business logic off the `shop` field of `WebhookMetadata`.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) into the value that is HMAC-verified, or otherwise cross-check the header-derived `shop` against an independently trusted source (e.g., verify the shop is associated with a valid, previously-stored session/access token before trusting webhook content for that shop) rather than trusting the header value on its own once only the body's signature has been checked.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com`, a shop they legitimately control.
2. Shopify sends a webhook to the app: body `B`, header `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`, header `X-Shopify-Hmac-Sha256: HMAC(client_secret, B)`.
3. Attacker captures `B` and the valid HMAC value.
4. Attacker crafts a new HTTP POST to the app's webhook endpoint with the same body `B` and the same valid HMAC header, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
5. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `HMAC(client_secret, B)` against the header value — both untouched from step 2. [5](#0-4) 
6. `handler.handle` is invoked with `shop: "victim-shop.myshopify.com"` and attacker-controlled body `B`, even though `victim-shop` never sent this webhook. [6](#0-5)

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
