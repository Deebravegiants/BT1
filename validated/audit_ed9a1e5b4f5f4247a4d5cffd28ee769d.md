### Title
Webhook shop-domain header is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the raw request body, but the `shop` value that the app relies on to identify which tenant the webhook belongs to is taken from an HTTP header that is never included in the signed payload. Because the signing secret (`api_secret_key`) is the same for every shop that has a given app installed, a shop owner (an unprivileged, non-credentialed actor with respect to *other* merchants' data) who receives a legitimate, correctly-signed webhook for their own store can replay that same body/HMAC pair to the app's webhook endpoint while substituting the `x-shopify-shop-domain` (or `shopify-shop-domain`) header of a victim shop. The signature check still passes because it never touched the header, and the handler is invoked believing the data belongs to the victim tenant.

### Finding Description
`ShopifyAPI::Webhooks::Request` extracts `shop` from a header and exposes it independently of the HMAC: [1](#0-0) 

Its `to_signable_string` — the value that is actually HMAC-verified — returns only `@raw_body`: [2](#0-1) 

`Registry.process` validates the HMAC and then immediately forwards `request.shop` to the app's handler as trusted tenant context, without any additional binding check between the signed body and the header-derived shop: [3](#0-2) 

`WebhookMetadata.shop` is documented and used by consuming apps as the authoritative shop identifier for routing/storing the payload: [4](#0-3) [5](#0-4) 

The identity binding that is expected to hold is: `shop delivered in the header == shop the HMAC signature was actually computed for`. Since `HmacValidator.validate_signature` only recomputes the HMAC over `verifiable_query.to_signable_string` (the raw body) and compares it against the received HMAC, the equality that is actually enforced is only `hmac(body, secret) == received_hmac`, which is silent on `shop`: [6](#0-5) 

Because `api_secret_key` is shared by the app across every shop that installs it, any merchant who legitimately receives a webhook (with a valid HMAC over some body) can capture that body+HMAC pair and resend it to the app's public webhook URL with an arbitrary `shop-domain` header value. The verification step passes, and the handler is invoked with `data.shop` set to whatever the attacker chose, while `data.body` is content the attacker controls the timing/shape of (or, at minimum, controls which of their own genuinely-signed bodies is replayed against a different shop label).

### Impact Explanation
This crosses a tenant boundary: an attacker with no privileges on the victim's Shopify store can cause the application to process attacker-supplied/attacker-timed webhook data as though it originated from the victim shop. Depending on how the host app implements its `handle` method (as universally recommended and shown in this gem's own docs — using `data.shop` to key database writes, trigger per-shop side effects, or invalidate/update per-shop state), this can lead to cross-tenant data corruption, spoofed events being attributed to a shop the attacker doesn't control, or forced re-processing/duplication under a victim's identity. This matches the "cross-tenant access" criterion because the confusable field (`shop`) is exactly the value host applications use as their session/tenant key when acting on webhook data, per this gem's own documented usage pattern.

### Likelihood Explanation
Likelihood is high for any attacker who can install the target app on their own store (the normal, unprivileged path for installing a Shopify app) — which grants them a stream of legitimately-signed webhooks. No secret material, elevated privilege, or credential theft is needed beyond normal app installation; only network access to the app's public webhook endpoint and the ability to replay an HTTP request with modified headers is required.

### Recommendation
Bind the header-derived `shop` (and other trust-relevant headers like `topic`/`webhook-id`) into the value that is HMAC-verified, or otherwise cross-check the header shop against an independently-trusted source (e.g., verify the shop is a valid, currently-registered installation and correlate the webhook body's own shop-identifying fields, if present, against the header) before trusting `request.shop` for tenant-scoped operations. At minimum, update `Utils::VerifiableQuery`/`Webhooks::Request#to_signable_string` so the signable string incorporates the shop domain header, and document to consuming apps that `data.shop` must not be treated as authenticated unless this binding is enforced.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker-shop.myshopify.com` and configures a topic (e.g. `orders/create`) to be delivered to the app's public webhook endpoint.
2. Attacker triggers or waits for a real event, capturing the genuine request Shopify sends, including:
   - `raw_body` (e.g., `{"id":1,...}`)
   - `x-shopify-hmac-sha256: <valid HMAC of raw_body using the app's api_secret_key>`
   - `x-shopify-shop-domain: attacker-shop.myshopify.com`
3. Attacker resends this exact request to the app's public webhook endpoint but changes only the header:
   `x-shopify-shop-domain: victim-shop.myshopify.com`
4. `ShopifyAPI::Webhooks::Request.new` parses headers/body as usual; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `raw_body` only — the substituted `shop` header is never checked — and validation succeeds: [7](#0-6) 
5. The app's registered `WebhookHandler#handle` is invoked with `data.shop == "victim-shop.myshopify.com"` even though the payload actually originated from the attacker's own store, letting the attacker inject data/events attributed to a shop they do not control.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-38)
```ruby
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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
