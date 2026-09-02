### Title
Webhook shop/topic/webhook-id/api-version headers are not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the raw request body, then trusts unauthenticated request headers — specifically `shop-domain`, `topic`, `webhook-id`, and `api-version` — to route and label the event. Because the HMAC only binds the body to the shared `api_secret_key`, and that secret is common to every shop that has installed the app, any shop that has the app installed can forge the shop identity of an unrelated shop while keeping a legitimately-signed body, breaking the binding between "HMAC-verified sender" and "shop attributed to the event."

### Finding Description
`Utils::HmacValidator.validate` computes the signature only from `to_signable_string`, and for webhooks that method returns just the raw body: [1](#0-0) 

The `shop`, `topic`, `webhook_id`, and `api_version` values are pulled directly from HTTP headers and are never included in the signable string: [2](#0-1) 

`Registry.process` validates only the HMAC (i.e., only the body) and then dispatches the handler using the unauthenticated `request.shop` and `request.topic`: [3](#0-2) 

The equality the code implicitly assumes is:

`sender authenticated by HMAC(secret, body) == shop identity attributed to the event (request.shop header)`

This equality does not hold: `api_secret_key` is shared across every shop/tenant that has this app installed, so the HMAC only proves "some installer of this app sent this body with the correct client secret" — it does **not** prove which shop the body/action belongs to. Any merchant who installs the app on their own store can trigger a genuine, correctly-HMAC'd webhook delivery for their own store, then replay/resubmit that request to the app's webhook endpoint with the `x-shopify-shop-domain` header changed to a victim shop's domain. `Utils::HmacValidator.validate` will still pass (it only checks the body against the shared secret), and `Registry.process` will hand the (attacker-controlled) body to the handler tagged with the victim's shop, topic, and webhook id of the attacker's choosing.

### Impact Explanation
This breaks the tenant boundary the webhook mechanism is supposed to enforce: an app that persists webhook data keyed by `WebhookMetadata#shop` (as constructed directly from the unauthenticated header) will attribute the attacker's forged event/topic/body to the victim shop. Depending on how the host app consumes `WebhookMetadata`, this can lead to cross-tenant data corruption or cross-tenant action execution (e.g., a fake `app/uninstalled`, `orders/create`, or `customers/data_request` event being processed under a victim shop's identity), which falls under "cross-tenant access."

### Likelihood Explanation
Exploitation requires only that the attacker be a legitimate, unprivileged installer of the app on their own shop — no access to `api_secret_key`, access tokens, or any other privileged material is needed. They only need to observe/capture one legitimately delivered webhook request (body + valid HMAC) for their own store and resend it with a modified `shop-domain` (and optionally `topic`/`webhook-id`) header to the app's public webhook endpoint. This is a realistic, low-effort attack path reachable directly through the gem's documented webhook processing API.

### Recommendation
Bind the identity fields used for routing/attribution into the signed material, or otherwise authenticate them independently of client-controlled headers:
- Have `Request#to_signable_string` include `shop`, `topic`, `webhook_id`, and `api_version` (or verify these against a signed source, such as looking up the webhook subscription server-side by `webhook_id` via the Admin API rather than trusting headers).
- At minimum, document/require host applications to verify `request.shop` against the shop that actually owns the active session/webhook subscription (e.g., cross-check with a per-shop registered webhook id) before trusting the attributed shop, rather than relying on HMAC-of-body alone as proof of shop identity.

### Proof of Concept
1. App is installed on `attacker-shop.myshopify.com` and receives a legitimate webhook (e.g., `products/update`) with a valid `x-shopify-hmac-sha256` computed by Shopify over the JSON body using the app's `api_secret_key`.
2. Attacker resends the exact same body and HMAC to the app's webhook endpoint but changes `x-shopify-shop-domain` to `victim-shop.myshopify.com` (and optionally the topic/webhook-id).
3. `Utils::HmacValidator.validate` succeeds because it only checks `OpenSSL.secure_compare(computed_signature, hmac)` against the raw body [4](#0-3) .
4. `Registry.process` invokes the registered handler with `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` [5](#0-4) , causing the host application to process the event as if it originated from `victim-shop.myshopify.com`.

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
