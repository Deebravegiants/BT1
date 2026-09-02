## Title
Webhook `shop`, `topic`, and `webhook_id` are trusted despite not being covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats a webhook request as authenticated once its HMAC validates, and then hands the caller-controlled `shop`, `topic`, `webhook_id` and `api_version` header values to the app's handler as if Shopify had vouched for them. In reality the HMAC signs only the raw body, not these headers, so the identity binding "HMAC valid ⇒ headers came from Shopify for this shop/topic" does not hold.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

while `shop`, `topic`, `webhook_id`, and `api_version` are all read straight from HTTP headers with no cryptographic binding to the body or to each other: [2](#0-1) 

`HmacValidator.validate` computes and compares the HMAC only over `to_signable_string` (i.e. the body): [3](#0-2) 

`Registry.process` validates that HMAC and then, without any further check, trusts `request.topic` to select the handler and forwards `request.shop`, `request.webhook_id`, `request.api_version` straight into the app's business logic: [4](#0-3) 

The identity binding that should hold is:
`HMAC-SHA256(api_secret_key, body) valid` ⇒ `(shop-domain header, topic header, webhook-id header) == the values Shopify actually sent for that body`.

That binding is false: the same `api_secret_key` is shared by every shop installed on the app, and the headers are never mixed into the signed material. Any party who can obtain one valid `(raw_body, hmac)` pair for the app (e.g. a merchant who has installed the app and receives Shopify's "send test webhook" payload for their own shop, or any legitimately delivered webhook they can capture) can replay that exact body and HMAC to the app's shared webhook endpoint while substituting an arbitrary `shopify-shop-domain` and `shopify-topic` header. The gem's own documentation asserts that `Registry.process` "will verify the request did indeed come from Shopify," which is not true for the shop/topic attribution, only for the body content.

### Impact Explanation
This lets an unprivileged, already-onboarded merchant (attacker-controlled tenant on a shared multi-tenant app) forge webhook deliveries that are attributed to a different shop than the one that actually produced them. Because `handler.handle` receives `shop: request.shop` taken verbatim from the unauthenticated header, the app's persistence/business layer can be made to record, act on, or overwrite data under another merchant's identity — a cross-tenant confusion/cross-tenant access primitive, satisfying the "Critical: cross-tenant access" impact bar.

### Likelihood Explanation
Exploitation requires only: (1) being a legitimate (if malicious) tenant of the same multi-tenant app so as to obtain one valid `(body, hmac)` pair via Shopify's own webhook delivery or "send test notification" feature, and (2) sending an HTTP POST to the app's public webhook callback URL with forged `shopify-shop-domain`/`shopify-topic`/`shopify-webhook-id` headers. No access token, `client_secret`, or privileged credentials are required — this is reachable by any unprivileged internet user who can install the target app on their own store.

### Recommendation
Bind the routing/attribution headers into the signed material (or otherwise cryptographically bind them), and/or require the host application to cross-check `request.shop` against a shop that has an active, registered webhook subscription/session for the `webhook_id` before invoking the handler, rather than trusting the header once the body-only HMAC passes. At minimum, document prominently that `shop`, `topic`, and `webhook_id` are NOT authenticated by `HmacValidator` and must be independently verified by the host app (e.g., against known installed shops) before being trusted.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` (both shops share the same app `api_secret_key`).
2. Attacker triggers (or captures) a legitimate webhook delivery for topic `customers/update`, obtaining a valid `raw_body` and its `x-shopify-hmac-sha256` value, both computed with the shared `api_secret_key`.
3. Attacker POSTs the same `raw_body` and the same HMAC header to the app's public webhook endpoint, but sets:
   - `x-shopify-shop-domain: victim-shop.myshopify.com`
   - `x-shopify-topic: customers/update` (unchanged, so body schema matches)
4. `ShopifyAPI::Utils::HmacValidator.validate(request)` returns `true` because only the body was checked.
5. `ShopifyAPI::Webhooks::Registry.process` invokes the registered handler with `shop: "victim-shop.myshopify.com"`, causing the app to process attacker-supplied customer data as if it belonged to `victim-shop`.

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
