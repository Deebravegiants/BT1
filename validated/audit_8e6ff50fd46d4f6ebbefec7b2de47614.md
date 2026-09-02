### Title
Webhook `shop` tenant identifier is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, so the HMAC verified by `Utils::HmacValidator.validate` in `ShopifyAPI::Webhooks::Registry.process` proves only that the *body bytes* were signed with the app's shared `client_secret` — it says nothing about which shop the request claims to be from. The `shop` value that is handed to the app's webhook handler as the tenant identifier is read from the `x-shopify-shop-domain` header, which sits completely outside the signed payload.

### Finding Description
The intended identity binding is: `shop_domain_used_for_tenant_routing == shop_domain_the_HMAC_secret_actually_authenticates_for`. In this gem, that binding is broken:

- `Request#hmac` decodes the `hmac-sha256` header [1](#0-0) 
- `Request#to_signable_string` signs only `@raw_body`, excluding every header, including `shop-domain` [2](#0-1) 
- `Request#shop` is read straight from the (unauthenticated w.r.t. HMAC) `shopify-shop-domain`/`x-shopify-shop-domain` header [3](#0-2) 
- `Registry.process` validates only that the body's HMAC is correct, then immediately trusts `request.shop` as the tenant identity for the handler [4](#0-3) 

Because the same `client_secret` HMAC key is shared across every shop that installs the app, any tenant that legitimately receives one authentic webhook (i.e., every merchant who installs the app receives webhooks whose HMAC they can capture) possesses a body+HMAC pair that is valid for *any* shop, since the header carrying the shop identity is never part of the signed material. An attacker who controls the install of the app for their own shop can replay a legitimate `(raw_body, hmac)` pair to the app's webhook endpoint while substituting `x-shopify-shop-domain` for a victim shop. `HmacValidator.validate` still returns `true` because it only recomputes the HMAC over `@raw_body`, and `Registry.process` passes the attacker-chosen `shop` value straight into `WebhookMetadata`, which is what handler code is documented to rely on for tenant identification.

### Impact Explanation
This breaks the tenant boundary the webhook handling API is supposed to enforce: an app's webhook handler is documented to trust `data.shop` as "The shop domain of the webhook" [5](#0-4) , and that value is used by handlers to route/apply data to the correct shop's records (as illustrated in the docs' example handler) [6](#0-5) . Since the gem gives applications no way to distinguish "the body was HMAC-authentic" from "the body belongs to the claimed shop," any consumer that relies solely on `Registry.process`/`Request#shop` for tenant scoping can be made to process a validly-HMAC'd payload under another merchant's shop domain — i.e., cross-tenant data injection/impersonation via webhook processing.

### Likelihood Explanation
Exploitation requires the attacker to be a legitimate (even free, uninstalled-after) merchant/installer of the target app so they can capture one authentic `(body, hmac)` pair from their own webhook traffic, then POST it to the app's webhook route with a forged `shop-domain` header — no access token, `client_secret`, or privileged account is needed, matching the "unprivileged internet user" threat model. This is a realistic, low-effort replay since webhook endpoints are public HTTP routes and headers are attacker-controlled in the request they send.

### Recommendation
Bind the shop identity into the verified signature material: include the `shop-domain` (and ideally `webhook-id`/`topic`) in `to_signable_string`, or independently verify that `request.shop` corresponds to a shop with an active session/registration known to the app before dispatching to the handler. At minimum, document prominently that `Registry.process` does not authenticate the `shop` header and that consuming applications must cross-check it against their own installed-shop records before trusting it for tenant-scoped operations.

### Proof of Concept
1. App A is installed on `attacker.myshopify.com` and on `victim.myshopify.com`, both using the same app `client_secret`.
2. Attacker triggers/receives a legitimate webhook for `attacker.myshopify.com`, capturing `raw_body` and the correct `X-Shopify-Hmac-Sha256` value.
3. Attacker POSTs to the app's webhook endpoint with the same `raw_body` and `X-Shopify-Hmac-Sha256`, but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` parses the forged header set; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC only over `raw_body` [7](#0-6)  — it passes.
5. `handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, ...))` is invoked with `shop == "victim.myshopify.com"`, even though the payload actually originated from/for `attacker.myshopify.com` [8](#0-7) .

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

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

**File:** docs/usage/webhooks.md (L12-14)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
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
