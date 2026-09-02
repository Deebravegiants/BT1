### Title
Webhook shop/topic identity trusted from unauthenticated headers while HMAC only covers the raw body - (File: lib/shopify_api/webhooks/request.rb)

### Summary
The external report describes a value used to gate an action (`proposalThreshold`) that does not match what is actually verified/enforced. The corresponding class of bug in this gem is a field that is *acted upon* but *not covered by the cryptographic check* used to authenticate the message. In `ShopifyAPI::Webhooks::Request`/`Registry`, the HMAC signature validated by `Utils::HmacValidator` is computed only over the raw request body, while the `shop` (and `topic`, `webhook_id`, `api_version`) values that the handler treats as authenticated, tenant-identifying data come from unauthenticated HTTP headers.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, `topic`, `webhook_id`, and `api_version` are all read straight from HTTP headers with no cryptographic binding to the HMAC: [2](#0-1) 

`Registry.process` validates the HMAC (body-only) and then forwards the *unauthenticated* `request.shop` value straight to the app's handler as trusted webhook metadata: [3](#0-2) 

The documented contract tells host apps that `data.shop` is "The shop domain of the webhook" and shows it being used directly to key work (e.g., `perform_later(topic: data.topic, shop_domain: data.shop, ...)`), implying it is a trusted, authenticated value: [4](#0-3) 

The equality that is supposed to hold is: `shop asserted by the signed message == shop the handler acts on`. Because the HMAC only signs `@raw_body`, that equality is never actually checked by the gem — `request.shop` is simply copied from the `X-Shopify-Shop-Domain` (or `shopify-shop-domain`) header, which is not part of the signed material.

### Impact Explanation
Since `shop`, `topic`, `webhook_id`, and `api_version` are outside the HMAC, an attacker who can obtain any single valid `(raw_body, hmac)` pair signed with the app's real secret (for example, from their own installed development store, which is not a privileged secret) can replay that exact body+signature to the app's public webhook endpoint while substituting the `shop-domain` header for a victim shop. `Utils::HmacValidator.validate` will report success (it never inspects the shop header), and `Registry.process` will hand the handler a `WebhookMetadata` claiming the payload belongs to the victim shop. If the host application uses `data.shop` (as the documentation itself instructs) to select which merchant record/session/credentials to mutate, this is a cross-tenant data-integrity issue: an attacker-controlled body ends up being attributed to and processed against another tenant's identity. This matches the "Critical - cross-tenant access" impact category, since the boundary broken is exactly a shop/tenant identity binding that the gem is expected to authenticate but does not.

### Likelihood Explanation
Likelihood is bounded by the fact that the attacker must first possess at least one legitimately-signed `(body, hmac)` pair — e.g., from their own store's webhook deliveries for the very same app (any developer/merchant can install a public app and receive real signed webhooks). No `api_secret_key`, access token, or privileged access is required to obtain this pair; it is simply the attacker's own webhook traffic. Constructing the replay only requires re-POSTing the same raw body and HMAC header while changing the shop-domain header, both of which are attacker-controlled request properties reachable over the internet.

### Recommendation
Include `shop`, `topic`, `webhook_id`, and `api_version` in the HMAC-signed material (or otherwise authenticate them, e.g. by validating the `shop` against a session store established during OAuth) before exposing them as trusted fields on `WebhookMetadata`. At minimum, update `Utils::HmacValidator`/`VerifiableQuery` so the signable string for webhook requests binds the header values that are used for tenant attribution, matching Shopify's guarantee model, and clarify in `docs/usage/webhooks.md` that `data.shop` must not be trusted for tenant-sensitive actions without independent verification.

### Proof of Concept
1. Attacker installs the target app on their own development store and captures a legitimate webhook delivery: raw body `B` and header `X-Shopify-Hmac-Sha256: H` (valid for the app's real `api_secret_key`), together with `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`.
2. Attacker sends a new HTTP POST to the same app webhook endpoint with the identical body `B` and identical `X-Shopify-Hmac-Sha256: H`, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses headers, and `Utils::HmacValidator.validate` succeeds because it only recomputes the HMAC over `@raw_body` (`to_signable_string`) — see `lib/shopify_api/webhooks/request.rb` lines 35-38 and `lib/shopify_api/utils/hmac_validator.rb` lines 26-31.
4. `Registry.process` calls the handler with `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: parsed_body, ...)` (`lib/shopify_api/webhooks/registry.rb` lines 188-200), even though the payload was never actually sent by Shopify on behalf of `victim-shop`.
5. Any host application logic that keys work off `data.shop` (as shown in the gem's own webhook documentation example) will now act as if this attacker-supplied payload originated from the victim tenant.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-33)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end

      sig { returns(String) }
      def api_version
        T.cast(shopify_header("api-version"), String)
      end

      sig { returns(String) }
      def webhook_id
        T.cast(shopify_header("webhook-id"), String)
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
