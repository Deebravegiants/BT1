### Title
Webhook Shop-Domain Header Not Covered by HMAC Signature Enables Cross-Tenant Webhook Spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook solely by validating the HMAC over the raw request body, but the `shop` identity that is subsequently handed to the app's handler is read from an HTTP header that is never included in the signed material. The binding the gem implicitly claims to enforce — "the shop the HMAC authenticates" == "the shop the handler acts on" — does not hold, because `to_signable_string` only covers the body.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is derived from the `shopify-shop-domain` / `x-shopify-shop-domain` HTTP header, which is not part of that signable string: [2](#0-1) 

`HmacValidator.validate` computes and compares the HMAC only over `verifiable_query.to_signable_string`: [3](#0-2) 

`Registry.process` uses this HMAC check as the sole authenticity gate, then immediately forwards `request.topic`, `request.shop`, `request.webhook_id`, and `request.api_version` — none of which are covered by the HMAC — to the app's handler as trusted values: [4](#0-3) 

The documented usage pattern explicitly tells integrators to trust `data.shop` for tenant-scoped work (e.g. `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`), so the shop value flowing out of `Registry.process` is treated as an authenticated tenant identifier by design: [5](#0-4) 

Because the equality "shop bound by HMAC" == "shop used to attribute/process the webhook" is broken, any party who can obtain one valid `(raw_body, hmac)` pair — e.g., their own shop's genuine webhook delivery, which they fully control as the resource owner and recipient — can resend that exact body/HMAC pair to the app's public webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header value. `HmacValidator.validate` will still pass (the body is unchanged), and `Registry.process` will dispatch the handler with `shop` set to the attacker-chosen value instead of the shop that actually owns the payload.

### Impact Explanation
This is a cross-tenant identity-binding break: an unprivileged internet user who merely has one legitimate webhook delivery (from their own store) can cause the app to process/attribute that payload as belonging to a different, arbitrary shop of their choosing. Depending on how the host app uses `data.shop` (queuing background jobs, updating tenant-scoped records, looking up sessions by shop, cache invalidation, etc.), this enables cross-tenant data confusion or corruption without needing the app's `client_secret`, an access token, or any other credential — only a single genuine webhook of the attacker's own.

### Likelihood Explanation
Reachability requires only: (1) the app has the webhook endpoint publicly reachable (standard deployment, as documented), and (2) the attacker has installed the app on any shop they control (a normal, low-privilege action any merchant can take) to obtain one authentic `raw_body`+`hmac` pair. From there the header substitution and replay requires no secret material. This is a design-level gap in the gem's `Request`/`Registry`/`HmacValidator` trio rather than a host-app misuse: the API contract (`data.shop`) implies an authenticated value, but the code never binds it to the signature.

### Recommendation
Include the shop domain (and ideally topic/webhook_id) in the HMAC-signed material verified by `HmacValidator`, or otherwise cryptographically bind the `shop` header to the request before trusting it (e.g., require the app to independently confirm the shop has an active session/install matching the header before acting, and document this as mandatory). At minimum, update `to_signable_string` in `lib/shopify_api/webhooks/request.rb` to incorporate the shop-domain header so that `Utils::HmacValidator.validate` fails if the header is altered relative to the originally signed request. Alternatively/additionally, harden `Registry.process` to reject payloads whose declared shop is not consistent with an install known to the host app, though that mitigation lives outside this gem.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and receives a genuine webhook delivery for that shop: body `B`, header `x-shopify-hmac-sha256: H` (valid for `B`), header `x-shopify-shop-domain: attacker-shop.myshopify.com`.
2. Attacker POSTs to the app's webhook endpoint with the same `B` and `H`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {...})` builds a request whose `to_signable_string` is still `B`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `HMAC(secret, B) == H`. [4](#0-3) 
5. The handler is invoked with `WebhookMetadata` where `shop == "victim-shop.myshopify.com"`, even though the payload actually originated from and pertains to `attacker-shop.myshopify.com`.

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

**File:** docs/usage/webhooks.md (L20-29)
```markdown
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
