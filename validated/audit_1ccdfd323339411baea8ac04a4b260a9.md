### Title
Webhook shop identity is not bound by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC only over the raw request body, while the `shop` (and `topic`/`webhook_id`) values used by `ShopifyAPI::Webhooks::Registry.process` and handed to the app's handler are read from unauthenticated HTTP headers. The gem verifies "this body was signed by Shopify" but never verifies "this body was signed *for this shop*", so the shop identity that the app trusts for tenant separation is not cryptographically bound to the payload it is attached to.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is read directly from the `shopify-shop-domain`/`x-shopify-shop-domain` header, entirely outside the signed material: [2](#0-1) 

`Registry.process` validates the HMAC over the body only, then immediately forwards the unauthenticated `request.shop` value to the handler as the tenant identifier: [3](#0-2) 

The documented usage pattern explicitly treats `data.shop` as a trusted per-tenant key, e.g. for routing/storing work by shop domain: [4](#0-3) 

The broken identity binding is:
`HMAC-verified(raw_body)` ⇏ `shop == request.shop`

Concretely, the check only proves `HMAC_secret(raw_body) == received_hmac`; it says nothing about which shop that body/hmac pair was issued for. Any attacker who can obtain one valid `(raw_body, hmac)` pair signed by the app's secret — trivially available to them as a legitimate, unprivileged merchant who has installed the app on their own store and thus receives real webhooks with valid HMACs for their own shop — can replay that exact body and HMAC to the app's public webhook endpoint while swapping only the `shopify-shop-domain` header to name a different (victim) shop. `HmacValidator.validate` still succeeds because it never inspects the shop header: [5](#0-4) 

The handler then receives `WebhookMetadata` claiming the victim shop while carrying the attacker's own body content, i.e. the app processes attacker-controlled data under another tenant's identity — a cross-tenant confusion condition.

### Impact Explanation
This falls under the Critical "cross-tenant access" category: an unprivileged app user (any merchant who installs the app) can cause the app to attribute forged/attacker-controlled webhook data to an arbitrary victim shop, because the only cryptographic guarantee (`HMAC(body)`) is decoupled from the value (`shop` header) that host applications are told to trust for tenant scoping.

### Likelihood Explanation
Likelihood is high for any app that relies on the documented `data.shop` field for tenant identification (as the gem's own docs recommend) without independently re-validating shop ownership against the registered webhook subscription. No secrets, tokens, or privileged access are required — only the ability to install the app on one's own shop (an unprivileged action) and send a crafted HTTP POST with the replayed body/HMAC and a different shop header to the app's public webhook endpoint.

### Recommendation
Bind the shop (and ideally topic/webhook_id) into the signed material, or otherwise cross-check the header-derived `shop` against an out-of-band trusted value (e.g., the shop associated with the specific webhook subscription/`webhook_id`, or a per-shop secret) before passing it to handlers. At minimum, document prominently that `data.shop` is not covered by the HMAC and must not be trusted for tenant scoping without additional verification.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and receives a legitimate webhook: body `B`, header `shopify-shop-domain: attacker.myshopify.com`, header `shopify-hmac-sha256: H` (valid HMAC of `B`).
2. Attacker POSTs to the app's webhook endpoint with the same body `B` and same `shopify-hmac-sha256: H`, but sets `shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` accepts the request (all required headers present).
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `@raw_body` (`B`) only and succeeds, since the shop header was never part of the signed string: [6](#0-5) 
5. The handler is invoked with `WebhookMetadata` whose `shop` is `victim.myshopify.com` but whose `body` is the attacker's own data, confirming the identity/body binding is not enforced.

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
