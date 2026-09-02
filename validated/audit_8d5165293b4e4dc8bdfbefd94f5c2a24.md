### Title
Webhook `shop` field is not covered by the HMAC signature, allowing cross-tenant shop spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook by validating only the raw request body against the HMAC header, but the `shop` value that is handed to the app's webhook handler and used to identify the tenant is read directly from an unauthenticated header, breaking the identity binding `HMAC-verified bytes == data acted on`.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop` accessor simply reads the `shopify-shop-domain`/`x-shopify-shop-domain` header with no cryptographic binding to the signed body: [2](#0-1) 

`Registry.process` validates the HMAC over the request (i.e., only the body) and then immediately trusts `request.shop`, `request.topic`, `request.webhook_id`, and `request.api_version` — none of which are covered by that HMAC — to build the metadata that is passed to the app's handler: [3](#0-2) 

`Utils::HmacValidator.validate` computes the signature purely from `verifiable_query.to_signable_string` (the raw body) and the shared secret, confirming the header fields are entirely outside the signed scope: [4](#0-3) 

Documentation confirms `data.shop` is meant to identify which merchant/tenant the webhook belongs to and is exactly the value handler code is expected to key off of (e.g., `perform_later(topic: data.topic, shop_domain: data.shop, ...)`): [5](#0-4) 

Because only the body bytes are authenticated, an unprivileged internet user who controls a Shopify store (and can therefore legitimately trigger a webhook delivery with a genuine HMAC for their own shop/body) can capture that genuine `(raw_body, hmac)` pair and replay it to the app's webhook endpoint with the `shopify-shop-domain` header rewritten to a victim shop's domain. The signature still validates (it only covers the body), but the app's handler will process the payload as if it belongs to the victim tenant, since `data.shop` is the only tenant discriminator exposed to the handler and it is unauthenticated.

This is the same bug class as the report: a field that is *acted upon* (`shop`, used for tenant attribution) is not covered by the authentication mechanism (`HMAC`) that is supposed to bind the whole message to its origin, letting an attacker desynchronize which identity a verified payload is attributed to — a cross-tenant identity-binding break, analogous to the ACP-77 case where the FCHAIN and P-Chain validator identity states become mismatched because an unguarded field lets the attacker walk state machines out of sync with what was actually authenticated.

### Impact Explanation
This crosses a tenant boundary: data validly signed for shop A (attacker's own store) can be misattributed to shop B (an arbitrary victim store) purely by header manipulation, with the gem's own `Registry.process`/`HmacValidator` offering no protection against this because the signature never covered the shop identity. Any host app that follows the documented pattern of trusting `data.shop` for tenant-scoped writes (the exact pattern shown in this gem's own documentation) is exposed to cross-tenant data injection/corruption. This matches the "cross-tenant access" Critical impact category, since it lets an attacker's own legitimately-signed webhook events be attributed to and processed under a different merchant's identity.

### Likelihood Explanation
Exploitation requires only: (1) the attacker operates their own Shopify store (an ordinary, unprivileged capability — no special credentials, no access token, no `api_secret_key`), (2) the attacker triggers an action in their own store to generate a real webhook with a valid HMAC, and (3) the attacker replays the captured body+HMAC to the app's public webhook endpoint with a modified shop-domain header. No secret material, TLS interception, or social engineering is needed, and the flow uses only public, documented behavior of `ShopifyAPI::Webhooks::Registry.process` and `Request`.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) into the signable string, or otherwise cryptographically tie the header-derived tenant identity to the authenticated payload. If Shopify's real HMAC scheme genuinely only signs the body (matching Shopify's documented webhook verification, which does only sign the body), then `ShopifyAPI::Webhooks::Registry`/`WebhookMetadata` should not present `shop` as an implicitly trusted, standalone value for tenant attribution without clearly documenting that host applications must independently verify the `shop` value (e.g., against a known, previously-registered shop for that specific `webhook_id`/subscription) before using it to key any tenant-scoped operation. At minimum, update `docs/usage/webhooks.md` to explicitly warn that `data.shop` is not authenticated by the HMAC and must not be trusted for tenant attribution without additional verification.

### Proof of Concept
1. Attacker installs the app on their own store `attacker.myshopify.com` and performs an action that triggers a subscribed webhook topic (e.g., `orders/create`), producing a genuine webhook POST with body `B` and header `x-shopify-hmac-sha256: H` (a valid HMAC of `B` under the app's real `api_secret_key`) and `x-shopify-shop-domain: attacker.myshopify.com`.
2. Attacker captures this `(B, H)` pair.
3. Attacker sends a new POST to the app's public webhook endpoint with the same body `B` and same `x-shopify-hmac-sha256: H`, but sets `x-shopify-shop-domain: victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `HMAC(secret, B) == H` — this succeeds because `B` and `H` are unchanged.
5. The handler is invoked with `WebhookMetadata.new(topic: request.topic, shop: "victim.myshopify.com", body: JSON.parse(B), ...)`, so the app processes attacker-controlled data as though it originated from the victim's store. [3](#0-2)

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** docs/usage/webhooks.md (L10-30)
```markdown
If you want to register for an http webhook you need to implement a webhook handler which the `shopify_api` gem can use to determine how to process your webhook. You can make multiple implementations (one per topic) or you can make one implementation capable of handling all the topics you want to subscribe to. To do this simply make a module or class that includes or extends `ShopifyAPI::Webhooks::WebhookHandler` and implement the `handle` method which accepts the following named parameters: data: `WebhookMetadata`. An example implementation is shown below:

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
