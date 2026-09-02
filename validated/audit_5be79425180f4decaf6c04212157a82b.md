### Title
Webhook `shop` (and `topic`/`webhook-id`/`api-version`) identity fields are not covered by the HMAC signature, allowing cross-tenant shop spoofing of authenticated webhook payloads - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the `shop`, `topic`, `webhook_id`, and `api_version` values purely from HTTP headers, while `to_signable_string` — the value that `Utils::HmacValidator` actually verifies — is only the raw request body. [1](#0-0) [2](#0-1) 

### Finding Description
`Registry.process` treats a request as authentic solely based on `Utils::HmacValidator.validate(request)` succeeding: [3](#0-2) 

`HmacValidator.validate_signature` computes the HMAC over `verifiable_query.to_signable_string`, and `Request#to_signable_string` returns only `@raw_body`: [4](#0-3) [5](#0-4) 

Meanwhile `Request#shop`, `#topic`, `#webhook_id`, and `#api_version` are read straight from headers that are never part of the signed material: [6](#0-5) 

The identity binding that should hold is: `HMAC-verified(body, shop)` — i.e., the shop attributed to a webhook must be the same tenant whose secret-derived signature validated the body. Instead the code only proves `HMAC-verified(body)`; `shop` is an unauthenticated, attacker-supplied header that is trusted and passed straight into `WebhookMetadata` for the handler to act on: [7](#0-6) [8](#0-7) 

Because a single app's `api_secret_key` is shared across every merchant/tenant that installs the app (it's not per-shop), any merchant who has installed the app can capture a legitimately-signed webhook body that Shopify sent for their own store (a valid `body` + `hmac` pair, since HMAC only covers the body) and replay it to the app's webhook endpoint with the `X-Shopify-Shop-Domain` (or `Shopify-Shop-Domain`) header rewritten to a victim shop's domain. The signature still validates because the body is unmodified, but `Registry.process` will hand the handler a `WebhookMetadata` claiming the data belongs to the victim shop.

### Impact Explanation
This breaks the tenant boundary the HMAC is supposed to enforce: an unprivileged, already-onboarded merchant of the host application can make the webhook processing pipeline believe arbitrary attacker-chosen (but validly-signed) event data originated from a different shop. Any host application that keys per-shop state, records, or authorization decisions off `WebhookMetadata#shop` (as the library's own design encourages, since it is the only tenant identifier delivered with the webhook) can be tricked into writing/mutating data under, or associating actions with, a victim shop it never received the event from — a cross-tenant access impact.

### Likelihood Explanation
Likelihood is constrained by the precondition that the attacker must be a legitimate (if malicious) merchant of the same multi-tenant app so they can generate at least one validly-signed webhook body from their own store's activity, and must be able to POST directly to the app's webhook endpoint with custom headers (bypassing normal Shopify delivery, which the endpoint accepts since nothing ties the delivery to Shopify's IP or channel). Both conditions are realistic for any public SaaS app built on this gem, since webhook endpoints are internet-reachable HTTP endpoints and the header names are documented/public.

### Recommendation
Include the tenant/topic identity fields (at minimum `shop`, and ideally `topic`/`webhook_id`/`api_version`) in the HMAC-signed material, or otherwise cryptographically bind the header-derived `shop` to the signed body (e.g., verify a per-shop signature, or require the caller to additionally confirm the `shop` against a mac computed with a per-shop secret) before constructing `WebhookMetadata`. At minimum, document that `Registry.process` gives no authenticity guarantee over `request.shop`, `request.topic`, or `request.webhook_id`, and any consuming app must not use these header-derived values as an integrity-bearing tenant identifier.

### Proof of Concept
1. Attacker (already an installed merchant, tenant "attacker-shop.myshopify.com") triggers a legitimate action in their own store causing Shopify to deliver a genuine webhook to the app: headers include `X-Shopify-Hmac-Sha256: <valid-hmac-of-body>`, `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`, `X-Shopify-Topic: orders/create`, body `B`.
2. Attacker intercepts/replays this raw HTTP POST verbatim to the app's webhook endpoint, but overwrites `X-Shopify-Shop-Domain` to `victim-shop.myshopify.com` (and optionally the topic/webhook-id headers), leaving body `B` and the HMAC header untouched.
3. Server calls `ShopifyAPI::Webhooks::Registry.process(request)`. `HmacValidator.validate` succeeds because it only checks `OpenSSL::HMAC.hexdigest(secret, B)` against the unmodified HMAC header — see: [9](#0-8) 
4. `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` is built with `shop == "victim-shop.myshopify.com"` even though the signature only proves the body came from a holder of the shared app secret, not that the event pertains to `victim-shop`. The handler processes/stores data under the victim's tenant identity. [7](#0-6)

### Citations

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
