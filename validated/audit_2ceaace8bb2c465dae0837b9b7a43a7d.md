### Title
Webhook `shop`, `topic`, and `webhook_id` fields are trusted from unauthenticated headers while the HMAC only covers the raw body - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by verifying an HMAC over the raw request body [1](#0-0) . The `shop`, `topic`, `webhook_id`, and `api_version` values that the handler receives and acts on are read directly from HTTP headers and are never included in the signed content [2](#0-1) .

### Finding Description
`Utils::HmacValidator.validate` computes/verifies the signature using `verifiable_query.to_signable_string` [3](#0-2) . For `ShopifyAPI::Webhooks::Request`, `to_signable_string` returns only `@raw_body` [4](#0-3) , while `shop`, `topic`, `webhook_id`, and `api_version` are parsed straight from headers with no cryptographic binding to the HMAC [5](#0-4) .

`Registry.process` validates only the HMAC, then dispatches to the handler keyed by `request.topic`, passing `request.shop`, `request.topic`, and `request.webhook_id` unchanged into `WebhookMetadata` [1](#0-0) . The identity-binding equality the gem should enforce — "shop/topic bound to the signed payload" — does not hold: `hmac_signed_content == raw_body` but `handler_input.shop/topic/webhook_id == unauthenticated_header_value`.

The documented handler contract explicitly tells host applications to key business logic off `data.shop` and `data.topic` (e.g. `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`) [6](#0-5) , and documents that `process` "will verify the request did indeed come from Shopify" [7](#0-6)  — implying the whole request, including `shop`, is authenticated, when in fact only the body bytes are.

Because the webhook signing secret (`Context.api_secret_key` / the app's client secret) is shared across every shop that installs the app, any merchant who has installed the app receives real, validly-signed webhook deliveries for their own shop (a legitimate `raw_body` + `hmac` pair). Since the header fields are not bound to that signature, that same valid `(raw_body, hmac)` pair can be re-submitted directly to the app's webhook endpoint with a forged `shopify-shop-domain` header pointing at a different (victim) shop and/or a forged `shopify-topic`/`shopify-webhook-id`, and `Registry.process` will accept it as authentic and hand it to the handler labeled as coming from the victim's shop.

### Impact Explanation
This breaks the tenant boundary the gem is expected to guarantee for webhook data: the `shop` value that downstream application code relies on to select the tenant's session/data is not authenticated by this gem, only the body content is. Depending on how the host app uses `data.shop` (e.g., resolving which merchant's records to update, uninstall/GDPR handling, keyed webhook idempotency), this enables cross-tenant confusion — an attacker-controlled merchant can inject a webhook event that the host application attributes to a shop it does not control. This matches the "cross-tenant access" class of critical impact defined by the scan rules, since the gem is the layer responsible for authenticating webhook identity and it fails to bind the identity fields it hands to the caller.

### Likelihood Explanation
Exploitation requires only: (1) installing the app as an ordinary merchant to receive at least one legitimately signed webhook (an unprivileged action available to any Shopify merchant/developer), and (2) the ability to POST arbitrary headers to the app's public webhook endpoint (which by design must accept internet-originated POSTs from "Shopify", and the gem does not perform any additional network-origin check). No access token, `api_secret_key`, or privileged Shopify account is required — this is reachable by an ordinary internet user through the gem's own documented `Registry.process`/`Webhooks::Request` API, not by the host app deviating from documented usage.

### Recommendation
Bind the identity/routing fields into the signed payload verification, or explicitly document that `shop`, `topic`, and `webhook_id` are untrusted metadata that MUST be independently corroborated (e.g., cross-checked against a known/registered shop and an expected webhook_id/topic combination, with dedupe/replay protection) before being used to select tenant data. At minimum, `Request#to_signable_string` should not be presented as validating "the request" as a whole when only the body is covered, and `WebhookMetadata.shop` should be documented as unauthenticated unless separately verified by the host application against its own shop registry.

### Proof of Concept
1. App installs on `attacker-shop.myshopify.com`; Shopify sends a legitimate webhook: body `B`, headers `x-shopify-hmac-sha256: H`, `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-topic: orders/create`.
2. Attacker captures `(B, H)`.
3. Attacker POSTs to the app's webhook endpoint with the same body `B` and HMAC header `H`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com` (and optionally a different `x-shopify-topic`/`x-shopify-webhook-id`).
4. `Utils::HmacValidator.validate(request)` recomputes HMAC over `B` only and succeeds, since `H` was genuinely produced for body `B` [8](#0-7) .
5. `Registry.process` calls the registered handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", topic: <forged>, body: <parsed B>, ...)` [9](#0-8) , and the host application acts on the forged shop identity.

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L15-38)
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

**File:** docs/usage/webhooks.md (L19-30)
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
```

**File:** docs/usage/webhooks.md (L123-126)
```markdown
## Process a Webhook

To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:

```
