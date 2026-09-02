Based on my analysis, I've confirmed the key vulnerability pattern.

### Title
Webhook shop identity spoofing via unauthenticated `shop-domain` header not covered by HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , meaning the HMAC verification performed by `Registry.process` only proves that the request *body* was signed with the app's secret; it makes no cryptographic claim about the `shop` value [2](#0-1) . The `shop` value is read straight from the `x-shopify-shop-domain` / `shopify-shop-domain` HTTP header, which is fully attacker-controlled and outside the signed payload [3](#0-2) .

### Finding Description
This is the same bug class as the SP1Blobstream report: a field that determines identity/tenant scope (`trusted_block_height`/`target_block_height` there, `shop` here) is trusted without being bound to the cryptographically verified data. The binding that should hold is:

`shop value that HMAC authenticates == shop value the handler acts on`

In `HmacValidator.validate`, the signature is computed over `verifiable_query.to_signable_string`, and for `Webhooks::Request` that string is only the raw JSON body [4](#0-3) [1](#0-0) . The `shop` accessor, however, is sourced from a header, not the body [3](#0-2) . `Registry.process` verifies the HMAC and then immediately constructs `WebhookMetadata` using `request.shop` from the unauthenticated header, handing it to the app's handler as the trusted tenant identifier [2](#0-1) . The gem's own documentation instructs integrators to treat `data.shop` as the authoritative shop for that webhook body and to key follow-up work (e.g. job enqueueing, session lookups) off of it [5](#0-4) .

Because the header is not part of the signed content, any entity that can obtain one legitimately-signed webhook body+HMAC pair for shop A (e.g., an attacker who installs the app on their own store and receives their own webhooks) can retransmit that exact body+HMAC to the app's webhook endpoint while substituting `x-shopify-shop-domain` with victim shop B's domain. `HmacValidator.validate` will still return `true`, since the signature only vouches for the body bytes, not the header. The app then processes attacker-supplied body data as if it belongs to shop B.

### Impact Explanation
This breaks the tenant boundary the HMAC check is supposed to enforce: `shop` verified vs. `shop` acted upon diverge. Depending on how the host application uses `data.shop` (a pattern the gem's own docs recommend — passing it to job queues, or looking up the shop's session/access token to perform further actions), this enables cross-tenant data injection: an attacker-controlled payload can be attributed to and processed under a victim shop's identity. This matches the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Likelihood is high for any app that follows the gem's documented integration pattern verbatim: register as a normal (non-privileged) merchant on the app, receive legitimately HMAC-signed webhooks for one's own shop, then replay the same raw body with a modified shop header to the app's public webhook controller endpoint. No access to the app's `client_secret`, access tokens, or any privileged capability is required — only the ability to install the app as an ordinary merchant and control an HTTP client capable of replaying a captured request with a modified header.

### Recommendation
Bind the `shop` (and other identity-bearing headers such as `topic`/`webhook_id` if used for authorization decisions) into the signed material, or otherwise validate the header value against an independently-verified source (e.g., cross-check `shop` against the shop associated with the session/webhook subscription that was registered, rather than trusting the header verbatim). At minimum, document prominently that `data.shop` is unauthenticated and must not be used to select tenant-scoped credentials without additional verification.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and registers for a webhook topic (e.g. `orders/create`).
2. Shopify sends a legitimately signed webhook to the app's controller: body `B`, header `x-shopify-shop-domain: attacker.myshopify.com`, header `x-shopify-hmac-sha256: HMAC(secret, B)`.
3. Attacker captures this request and resends it to the same endpoint, keeping body `B` and the HMAC header unchanged, but replacing the header with `x-shopify-shop-domain: victim.myshopify.com`.
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `request.to_signable_string` (`= B`) and compares it to the unchanged, still-valid `hmac` header — validation passes [6](#0-5) .
5. The handler receives `WebhookMetadata` with `shop: "victim.myshopify.com"` and the attacker-controlled body `B`, and processes/enqueues it as if it genuinely originated from `victim.myshopify.com` [7](#0-6) .

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

**File:** docs/usage/webhooks.md (L12-29)
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
