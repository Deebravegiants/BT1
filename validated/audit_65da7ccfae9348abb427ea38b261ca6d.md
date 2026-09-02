### Title
Webhook `shop-domain` and `topic` headers are not covered by the HMAC signature, allowing cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, while `shop`, `topic`, `webhook_id`, and `api_version` are read from unauthenticated HTTP headers. `ShopifyAPI::Webhooks::Registry.process` trusts `request.shop` as the tenant identifier after validating only the body's HMAC. An attacker who possesses one genuine, validly-signed webhook delivery (e.g., from their own shop, which they can trigger themselves) can replay that exact body/HMAC pair to the app's webhook endpoint while substituting the `shopify-shop-domain` (and/or `shopify-topic`) header to point at a different shop, and the gem will accept it as authentic.

### Finding Description
The equality that should hold is: `shop header used by the app to attribute the webhook == shop actually authenticated by the HMAC`. In this gem that equality is broken.

- `Request#to_signable_string` signs only `@raw_body`: [1](#0-0) 
- `shop`, `topic`, `webhook_id`, and `api_version` are parsed straight from headers with no cryptographic binding to the body or to each other: [2](#0-1) 
- `Registry.process` validates only the HMAC of the body via `Utils::HmacValidator.validate`, then immediately uses the unauthenticated `request.shop`/`request.topic` to look up a handler and hand the data to it as the trusted tenant/topic: [3](#0-2) 
- `Utils::HmacValidator.validate_signature` computes the HMAC purely over `verifiable_query.to_signable_string` (i.e., the raw body for webhooks) and secure-compares it to the `hmac-sha256` header: [4](#0-3) 

Because none of `shop-domain`, `topic`, or `webhook-id` are part of the signed material, a body+HMAC pair that is valid for one webhook delivery (any topic, any shop, using the app's shared `api_secret_key`) remains HMAC-valid no matter what `shop-domain`/`topic`/`webhook-id` headers accompany it. The host application (via `WebhookMetadata`) receives `shop: request.shop` as if it were an authenticated fact.

### Impact Explanation
This breaks the tenant-identity binding for webhook delivery: `request.shop`, trusted by handlers as "this event happened on this shop," is not actually authenticated by the signature. Any multi-tenant app that keys per-shop side effects (e.g., app/uninstalled cleanup, order/customer sync, GDPR data requests) off `request.shop` from `WebhookMetadata` can be made to process attacker-supplied body content under a victim shop's identity, i.e., cross-tenant confusion/access — one of the listed Critical impacts.

### Likelihood Explanation
Exploitation requires only:
1. An attacker who is a legitimate merchant/developer running the app on their own shop (unprivileged relative to the target tenant), so they can trigger a real webhook and capture a genuine `(raw_body, hmac-sha256)` pair signed with the shared `api_secret_key`.
2. The ability to submit an HTTP request to the app's public webhook endpoint with the same body/HMAC but a forged `shopify-shop-domain` (and optionally `shopify-topic`) header pointing at another shop that uses the same app.

No access to the app's `api_secret_key`, access tokens, or the victim's credentials is needed — only a capture-and-replay of one's own legitimately signed webhook with header substitution.

### Recommendation
Bind `shop`, `topic`, and `webhook_id` into the signed/verified material (or otherwise independently verify shop identity, e.g., cross-check `request.shop` against the shop associated with the resolved session/subscription before dispatching), rather than trusting these headers purely because the (header-independent) body HMAC validates.

### Proof of Concept
1. Install the app on an attacker-controlled dev shop (`attacker.myshopify.com`) and let it deliver a real webhook, e.g. for `orders/create`. Capture the raw body `B` and its `X-Shopify-Hmac-Sha256: H` header — `H` is a valid HMAC of `B` under the app's shared `api_secret_key`.
2. Replay the request to the same webhook endpoint, keeping `raw_body = B` and `X-Shopify-Hmac-Sha256 = H`, but set:
   - `X-Shopify-Shop-Domain: victim.myshopify.com`
   - `X-Shopify-Topic: orders/create` (or any registered topic)
3. `Utils::HmacValidator.validate` succeeds because it only checks `B` against `H` [5](#0-4) , and `Registry.process` dispatches to the handler with `shop: "victim.myshopify.com"` and attacker-controlled body content, even though `victim.myshopify.com` never sent this webhook [6](#0-5) .

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
