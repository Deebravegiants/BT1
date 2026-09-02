### Title
Webhook shop-domain header is not covered by HMAC verification, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
This is a valid analog of the reported bug class. The reported issue is about an identity-relevant value (`contract_weights`) being trusted/acted upon at a point where its "safety" was assumed to have been enforced elsewhere, but the enforcement point (clearing `LAST_CLAIMED_EPOCH`) didn't actually cover every path that reaches the vulnerable usage. The analog here is an identity-binding gap of the same shape but in this gem's own code: the tenant identifier (`shop`) used by `ShopifyAPI::Webhooks::Registry.process` is taken from an HTTP header that is never included in the HMAC signature computation, so verifying the HMAC does not verify the shop.

### Finding Description
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery` with: [1](#0-0) 

`hmac` is derived from the `hmac-sha256` header, and `shop` is derived independently from the `shop-domain` header. However, `to_signable_string` — the exact byte content that is HMAC-verified — is only the raw body: [2](#0-1) 

`Registry.process` validates the HMAC over that signable string, then immediately trusts `request.shop` (from the unauthenticated header) as the tenant identifier passed to the app's handler: [3](#0-2) 

The documented contract for webhook handlers states `shop` is "The shop domain of the webhook" and shows it being used directly as the tenant/shop key for downstream processing: [4](#0-3) 

The identity binding the library implicitly claims to provide is:
`HMAC-valid(raw_body) == (topic, shop, body) authentically originated from that shop`

But the actual binding enforced is only:
`HMAC-valid(raw_body) == raw_body was produced with the app's api_secret_key`

The `shop` (and `topic`, `webhook_id`, `api_version`) headers are completely outside the signed content, so nothing cryptographically ties a given signed body to the shop header sent alongside it.

### Impact Explanation
Any actor who can install the app on their own shop (an unprivileged, non-victim tenant) will legitimately receive real webhook deliveries from Shopify with a valid HMAC computed over the body using the app's shared `api_secret_key`. Because the `X-Shopify-Shop-Domain` header is not part of what's signed, that same attacker can replay the exact same `raw_body` + `hmac-sha256` header to the app's webhook endpoint while substituting the `shop-domain` header with a victim shop's domain. `Utils::HmacValidator.validate` still succeeds (it only checks the body bytes against the secret), and `Registry.process` dispatches the payload to the handler labeled as belonging to the victim shop. This lets one tenant inject/spoof data attributed to another tenant, which the app may use to update per-shop state, trigger redactions, or influence other shop-scoped side effects — a cross-tenant identity-binding break.

### Likelihood Explanation
Exploitation requires no possession of the `api_secret_key`, no access token, and no privileged account: only that the attacker be a normal, legitimately-installed merchant/tenant of the app (or any actor able to capture one valid webhook delivery, e.g., their own store's webhook). They only need to intercept/replay their own already-valid webhook request while modifying an unauthenticated header. This is straightforward and requires only standard HTTP tooling.

### Recommendation
Bind the shop (and ideally topic/webhook id) into the material that is HMAC-verified, or otherwise require the caller/handler layer to cross-check the `shop` header against a set of shops actually known to be installed for this app before trusting it as a tenant key. At minimum, document explicitly and loudly in `docs/usage/webhooks.md` that `X-Shopify-Shop-Domain` is not authenticated by `Registry.process`/`HmacValidator.validate` and must be independently verified by the host application against its own installed-shop records before being used for any tenant-scoped action.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and triggers a webhook (e.g., updates a product), receiving from Shopify a POST with headers `X-Shopify-Hmac-Sha256: <valid-hmac>`, `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`, and some `raw_body`.
2. Attacker resends the identical `raw_body` and `X-Shopify-Hmac-Sha256` value to the app's webhook endpoint, but replaces `X-Shopify-Shop-Domain` with `victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses the headers/body; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only hashes `@raw_body` against the shared secret [5](#0-4) .
4. The handler receives `WebhookMetadata.new(topic:, shop: "victim-shop.myshopify.com", body:, ...)` and processes/stores the attacker's payload as if it came from the victim shop.

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

**File:** docs/usage/webhooks.md (L12-30)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook

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
```
