### Title
Webhook `shop` identity is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, then trusts the unauthenticated `x-shopify-shop-domain` header as the tenant identity passed to the app's handler. Because the HMAC never covers the shop header, any holder of one genuine `(body, hmac)` pair for the shared app secret — obtainable by simply installing the app on a store the attacker controls — can replay that exact body/HMAC pair while substituting an arbitrary victim shop domain, and the gem will report it to the handler as an authentic event for the victim shop.

### Finding Description
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery` with: [1](#0-0) 

Its `to_signable_string`, the only material the HMAC is computed over, returns just `@raw_body`: [2](#0-1) 

`shop` is read straight from the `x-shopify-shop-domain`/`shopify-shop-domain` header with no cryptographic binding to the signature at all: [3](#0-2) 

`Registry.process` validates the HMAC via `Utils::HmacValidator.validate`, which internally calls `verifiable_query.to_signable_string` (i.e., only the body) and `OpenSSL.secure_compare` against the computed HMAC-SHA256 of that body using the app's shared `api_secret_key`: [4](#0-3) 

After this check passes, `Registry.process` immediately forwards `request.shop` — the unauthenticated header — to the app's handler as the tenant identity: [5](#0-4) 

The library's own documentation states that `Registry.process` "will verify the request did indeed come from Shopify and then call the specified handler for that webhook," and instructs handlers to key business logic (e.g., `perform_later(topic:, shop_domain: data.shop, ...)`) directly on `data.shop`, i.e. it promises the `shop` field is trustworthy once `process` succeeds. The equality the gem is supposed to guarantee is:

`shop bound by the HMAC == shop delivered to the handler`

but the actual behavior is:

`shop covered by the HMAC (none) != shop delivered to the handler (raw header value)`

Since the same `api_secret_key` is shared across all shops that install a given app, any unprivileged attacker can install the app on a shop they control (e.g., a free Shopify partner/dev store), trigger a real webhook, capture the resulting genuine `(raw_body, hmac)` pair, and replay it against the app's webhook endpoint with the `shop-domain` header rewritten to a victim shop. The HMAC still validates (it only ever authenticated the body, which is unchanged), so `Registry.process` calls the handler with `WebhookMetadata#shop` set to the victim's domain while the body content is attacker-controlled data from the attacker's own store.

### Impact Explanation
This breaks the tenant boundary the gem is documented to enforce: an app relying on `data.shop` from a successfully-verified webhook to route work, update per-tenant records, or make follow-on authenticated calls will process attacker-supplied, attacker-shaped webhook payloads as if they originated from the victim tenant. This is a cross-tenant access/injection vulnerability, matching the "Critical - cross-tenant access" impact category, since the attacker completely controls the payload content associated with an arbitrary target shop and can do so on demand, repeatedly, and cheaply.

### Likelihood Explanation
Likelihood is high: the attacker needs no privileged access to the victim, no leaked secret, and no access token — only their own (free) shop installation of the target app and the ability to send an HTTP POST to the app's public webhook endpoint with a forged header. This requires nothing beyond capabilities available to any internet user who can install the same public app.

### Recommendation
Include the `shop` (and ideally `topic`, `webhook_id`, `api_version`) values in the signable material verified by the HMAC, or otherwise cryptographically bind the shop identity to the signed payload (e.g., verify `shop` against a per-shop webhook signing context or cross-check it against the shop stored for the associated session before dispatch), so that a valid HMAC over a body from shop A cannot be replayed as a valid event for shop B in `Registry.process`.

### Proof of Concept
1. Attacker installs the target app on a shop `attacker.myshopify.com` they control, so their store shares the same `client_secret`/`api_secret_key` used to sign webhooks.
2. Attacker triggers a real webhook (e.g., `orders/create`) and captures the raw POST body `B` and the `X-Shopify-Hmac-Sha256` header value `H` sent by Shopify — this is a valid `(B, H)` pair under the shared secret.
3. Attacker crafts a new POST to the same webhook endpoint using body `B` and header `X-Shopify-Hmac-Sha256: H` unchanged, but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {...})` is constructed; `Registry.process` calls `Utils::HmacValidator.validate`, which recomputes HMAC over `B` only and it matches `H`, so validation succeeds.
5. `Registry.process` calls `handler.handle(data: WebhookMetadata.new(..., shop: "victim.myshopify.com", body: parsed_body_of_B, ...))`, and the app's handler processes attacker-controlled data as though it were an authentic event for `victim.myshopify.com`.

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
