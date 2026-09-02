### Title
Webhook `shop`/`topic`/`webhook_id` fields are trusted for tenant identity without being covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`, `lib/shopify_api/utils/hmac_validator.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates a webhook's authenticity by checking only the raw request body against the HMAC signature. The `shop`, `topic`, and `webhook_id` values — which the library extracts from HTTP headers and forwards to the host application as trusted, tenant-identifying data — are never included in the signed material. Any request bearing a body/HMAC pair that is valid for the shared app `client_secret` (e.g., one legitimately generated for the attacker's own shop) can have its `shop-domain` header rewritten to name a victim shop, and the library will still accept it and hand the forged identity to the handler.

### Finding Description
`HmacValidator.validate` computes the signature over `verifiable_query.to_signable_string` and compares it with `OpenSSL.secure_compare`: [1](#0-0) 

For webhooks, `to_signable_string` is defined to be only the raw HTTP body — none of the Shopify headers are part of the signed string: [2](#0-1) 

`Registry.process` uses this same unauthenticated `request.shop` (along with `topic` and `webhook_id`) to build the `WebhookMetadata` passed to the app's handler, right after the HMAC check that only covers the body: [3](#0-2) 

The documentation explicitly instructs integrators to use `data.shop` as the tenant key when dispatching webhook work (e.g. `perform_later(topic: data.topic, shop_domain: data.shop, ...)`): [4](#0-3) 

The identity binding that should hold is: `shop that produced the HMAC-valid body == shop attributed to the event by the library`. Because the app's `client_secret` used to sign webhooks is shared across every shop that installs the app (it is not per-shop), and only the body is signed, an attacker who has their own installation of the app (and therefore receives real, validly-signed webhook deliveries for their own store) can take a genuine `body` + `hmac` pair and resend it to the app's public webhook endpoint with the `X-Shopify-Shop-Domain` (or `shopify-shop-domain`) header changed to a victim shop's domain. `Utils::HmacValidator.validate` still returns `true` (only the body is checked), and `Registry.process` forwards `shop: request.shop` — now the victim's domain — into the handler as if Shopify itself had reported this event for that shop.

### Impact Explanation
This breaks the tenant boundary that `WebhookMetadata.shop` is supposed to enforce. Any host application that follows this gem's own documented pattern of keying work (job enqueue, DB row lookups, cache invalidation, etc.) off `data.shop` can be made to process attacker-supplied webhook bodies under a victim shop's identity, i.e., cross-tenant access/data injection driven entirely through this gem's webhook processing path, without the attacker ever possessing the victim's access token or the app's `client_secret`.

### Likelihood Explanation
Exploitation requires only that the attacker control (or install) one instance of the target app — a normal, unprivileged capability for any Shopify merchant/developer — and be able to POST to the app's public webhook URL, which by design must be internet-reachable. No secret material belonging to the victim or the app owner is needed; only a legitimately-signed body from the attacker's own shop and header rewriting.

### Recommendation
Bind the trusted identity fields into the signed material, or otherwise cryptographically tie `shop`/`webhook_id`/`topic` to the HMAC check, instead of trusting header values that sit outside `to_signable_string`. At minimum, `Registry.process` should verify that the shop claimed in the headers is consistent with a shop the app actually has an active session/webhook registration for (e.g. cross-check against previously registered webhook IDs per shop) before invoking the handler, and the library should document clearly that `data.shop` is not authenticated by the HMAC so integrators do not use it as a sole tenant key.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and captures a real Shopify webhook delivery: raw body `B` and header `X-Shopify-Hmac-Sha256: H` (valid for the app's shared `client_secret`).
2. Attacker POSTs to the app's public webhook endpoint with the same body `B` and header `H`, but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` accepts the request (all required headers present).
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which only recomputes the HMAC over `B` — this still matches `H`, so validation passes: [5](#0-4) 
5. The handler is invoked with `WebhookMetadata.new(shop: "victim.myshopify.com", topic: ..., body: parsed(B), ...)`, and any app logic keyed on `data.shop` now runs under the victim's identity with attacker-chosen body content.

### Citations

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
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
