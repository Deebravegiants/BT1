This confirms the finding. `WebhookMetadata.shop` (documented at [1](#0-0)  and used directly by app handlers like `perform_later(topic: data.topic, shop_domain: data.shop, ...)` per the doc example) is populated straight from `Request#shop`, which reads the unauthenticated `shopify-shop-domain`/`x-shopify-shop-domain` header, while the HMAC only covers the raw body bytes.

### Title
Webhook `shop` identity is not covered by the HMAC, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, and `ShopifyAPI::Utils::HmacValidator` verifies the HMAC solely over that body. However, `ShopifyAPI::Webhooks::Registry.process` trusts `request.shop`, which is read directly from the `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header — a value that is never included in the signed bytes — and passes it unchecked into `WebhookMetadata` for the app's handler to act on.

### Finding Description
`Request#hmac` and `Request#to_signable_string` are defined as: [2](#0-1) [3](#0-2) 

`shop` is read independently from a header that is not part of `to_signable_string`: [4](#0-3) 

`HmacValidator.validate_signature` computes the signature only from `verifiable_query.to_signable_string` (the raw body) and compares it against `verifiable_query.hmac`: [5](#0-4) 

`Registry.process` validates the HMAC and then immediately forwards `request.shop` — the unauthenticated header value — to the app's handler without any additional binding check: [6](#0-5) 

The binding that should hold is: *the shop identity acted upon by the handler == the shop identity cryptographically proven by the signature*. Instead, the gem proves only "these body bytes were HMAC'd with `api_secret_key`" and separately asserts, without any proof, "this webhook belongs to shop X" from a plain header. Because `api_secret_key` is a single secret shared across every shop that installs the app (not shop-specific), any tenant of the app who receives one genuine webhook (with a legitimately Shopify-computed HMAC over some body) can capture that raw body + HMAC pair and resend it to the app's webhook endpoint with an arbitrary `X-Shopify-Shop-Domain` header value. The HMAC still validates (it only checks the body), so `Registry.process` accepts the request and calls the handler with `data.shop` set to the attacker-chosen shop. This is the same class of flaw as the reported `NodeRegistry.registerNodeFor` issue: signed data that omits the identity/tenant binding (there, `registryID`; here, the shop domain) can be replayed across tenants that the signer never intended to authorize. The library's own documentation instructs app authors to key their business logic directly off `data.shop` (e.g. `shop_domain: data.shop`) per [7](#0-6) , so this unauthenticated field is expected to be trusted as a tenant identifier by design of the gem's API.

### Impact Explanation
This breaks the shop-tenant boundary the gem is supposed to enforce for webhook delivery. A malicious or compromised merchant who legitimately uses the app (and therefore legitimately receives webhooks whose bodies are HMAC'd with the app's shared `api_secret_key`) can replay a captured body/HMAC pair while spoofing the `shop-domain` header to point at a victim shop. Any app that follows the gem's documented pattern of trusting `data.shop` to route/store/act on webhook data (creating records, invalidating caches, updating per-shop state) can be made to apply a foreign shop's data under the attacker-chosen shop's identity — a cross-tenant integrity issue reachable by any existing app installer, without needing `api_secret_key`, an access token, or any other privileged credential.

### Likelihood Explanation
Any shop that has installed the app already receives its own real webhooks with valid HMACs, so obtaining a body+HMAC pair requires no special access — just being one of potentially many installers of a multi-tenant app. Forging the `shop-domain` header requires nothing more than crafting an HTTP request to the app's public webhook endpoint, which is by definition unauthenticated and open to receive Shopify's calls. No cryptographic secret, brute force, or social engineering is needed.

### Recommendation
Bind the shop (and ideally topic/webhook-id) into the signed material, or otherwise verify it out-of-band: either recompute/validate `to_signable_string` to include the `shopify-shop-domain` header alongside the body, or cross-check `request.shop` against an app-controlled source of truth (e.g. an existing stored session/install record for that shop) before dispatching to handlers, and document this requirement clearly so handler implementations do not treat `data.shop` as authenticated on its own.

### Proof of Concept
1. Shop A installs the app and receives a genuine webhook: body `raw_body`, headers include `x-shopify-hmac-sha256: <valid hmac of raw_body>` and `x-shopify-shop-domain: shop-a.myshopify.com`.
2. Shop A's operator (or anyone with access to that webhook payload) resends the identical `raw_body` and identical `x-shopify-hmac-sha256` value to the app's webhook endpoint, but sets `x-shopify-shop-domain: shop-b.myshopify.com` (a victim shop also using the app).
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because the HMAC only ever covered `raw_body`, unaffected by the header change: [8](#0-7) 
4. The handler is invoked with `WebhookMetadata.new(..., shop: "shop-b.myshopify.com", ...)`, causing the app to process/store data as if it originated from Shop B, even though Shop B never sent this webhook.

### Citations

**File:** docs/usage/webhooks.md (L12-17)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook
```

**File:** docs/usage/webhooks.md (L19-29)
```markdown
```ruby
module WebhookHandler
  extend ShopifyAPI::Webhooks::WebhookHandler

  class << self
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
  end
end
```

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
