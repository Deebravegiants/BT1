Based on my investigation, I've confirmed the vulnerability in the webhook processing flow.

### Title
Webhook `shop-domain` header is not covered by HMAC verification, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , while `shop`, `topic`, `webhook_id`, and `api_version` are all read directly from HTTP headers, unauthenticated by the HMAC [2](#0-1) . `Registry.process` validates only the HMAC over the body and then forwards `request.shop` (and other header values) straight to the app's handler as trusted tenant-identifying data [3](#0-2) .

### Finding Description
The equality that should hold is: `shop domain bound by HMAC == shop domain acted upon by the handler`. Here it does not: the HMAC signature covers only the raw JSON body, never the `shop-domain`, `topic`, `webhook-id`, or `api-version` headers. Any unprivileged internet user can install the target app on their own store (a normal, unprivileged onboarding action for public apps) and thereby legitimately trigger Shopify to send a validly-HMAC-signed webhook (body + HMAC pair) to the app's public webhook endpoint. Because the header fields are outside the signed payload, the attacker can replay that exact body/HMAC pair to the same endpoint while substituting the `x-shopify-shop-domain` (and/or `x-shopify-topic`, `x-shopify-webhook-id`) header with an arbitrary value, e.g. a victim shop's domain. `Utils::HmacValidator.validate` still succeeds because it only recomputes the signature over `to_signable_string`, which is just the body [4](#0-3) . `Registry.process` then constructs `WebhookMetadata` using the spoofed `request.shop` and calls the host app's handler with it, treating it as an authenticated Shopify-originated value [5](#0-4) . Documentation explicitly instructs handler authors to trust `data.shop` as "The shop domain of the webhook" [6](#0-5) , and to use it directly for tenant-scoped work (e.g. `shop_domain: data.shop`) [7](#0-6) , without any indication that this field is unauthenticated.

### Impact Explanation
This is a cross-tenant identity binding break: data or events genuinely originating from the attacker's own shop can be attributed to a victim merchant's shop inside the host application, since the shop value the app trusts for tenant routing/authorization is not bound to the same signature that authenticates the payload. This falls under the "Critical - cross-tenant access" impact category, since an unprivileged actor (any user who can install the public app on a free/dev store) can make the app process attacker-controlled webhook payloads under a victim's shop identity, with no credentials or privileged access required.

### Likelihood Explanation
Likelihood is reasonably high in real deployments: `Registry.process` is the gem's documented, canonical entry point for webhook handling, and its consumer contract explicitly says `data.shop` identifies the tenant [8](#0-7) . Obtaining a legitimately signed (attacker's own shop) webhook body/HMAC pair requires nothing more than installing the app once, well within reach of any unprivileged internet user, and the webhook endpoint is by design a public, unauthenticated HTTP endpoint.

### Recommendation
Bind the `shop-domain` (and ideally `topic`/`webhook-id`) header values into the HMAC-signed payload, or validate `request.shop` against the set of shops for which the app currently holds an active/legitimate session/webhook registration before invoking the handler, so that a value outside the signed bytes can never be trusted as tenant identity. At minimum, `to_signable_string` in `lib/shopify_api/webhooks/request.rb` should incorporate all header fields that downstream handlers are told to trust.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com` (no special privilege needed for a public app).
2. Attacker triggers a webhook event on their own shop (e.g., creates an order), causing Shopify to `POST` a validly HMAC-signed body to the app's public webhook endpoint with headers `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-hmac-sha256: <valid signature over the body>`.
3. Attacker replays this exact `raw_body` and HMAC value to the same endpoint, but changes the `x-shopify-shop-domain` header to `victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate(request)` still succeeds because `to_signable_string` only returns `raw_body`, which is unchanged [1](#0-0) .
5. `Registry.process` calls the host handler with `WebhookMetadata.new(..., shop: "victim-shop.myshopify.com", ...)` [5](#0-4) , causing the app to process attacker-controlled data as if it belonged to the victim's store.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** docs/usage/webhooks.md (L10-17)
```markdown
If you want to register for an http webhook you need to implement a webhook handler which the `shopify_api` gem can use to determine how to process your webhook. You can make multiple implementations (one per topic) or you can make one implementation capable of handling all the topics you want to subscribe to. To do this simply make a module or class that includes or extends `ShopifyAPI::Webhooks::WebhookHandler` and implement the `handle` method which accepts the following named parameters: data: `WebhookMetadata`. An example implementation is shown below:

`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook
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
