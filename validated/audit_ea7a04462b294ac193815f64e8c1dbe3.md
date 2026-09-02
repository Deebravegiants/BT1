### Title
Webhook shop identity not bound to HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from only the raw request body [1](#0-0)  while the `shop` tenant identifier is read from the `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header, which is completely excluded from the signed bytes [2](#0-1) . `Webhooks::Registry.process` validates only that the body's HMAC matches, then trusts `request.shop` when dispatching to the app's handler [3](#0-2) .

### Finding Description
The identity binding that should hold is: `shop value cryptographically bound to the signed payload == shop value the handler acts on`. Here, `HmacValidator.validate` recomputes the HMAC over `verifiable_query.to_signable_string`, and for `Webhooks::Request` that method returns only `@raw_body` [1](#0-0) , ignoring every header, including `shop-domain` [2](#0-1) . `HmacValidator.validate_signature` only ever hashes that signable string against the app's `api_secret_key` [4](#0-3) .

Since the app's `api_secret_key` is the same for every shop the app is installed on (it is the app's client secret, not a per-shop secret), any legitimate merchant/tenant who has the app installed can capture one authentic webhook delivery (raw body + valid `x-shopify-hmac-sha256`) sent to their own shop, then resubmit that exact `(raw_body, hmac)` pair to the app's public webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header value (e.g., a victim tenant's domain). Because the shop header is not part of the signed bytes, `HmacValidator.validate` still returns `true`, and `Registry.process` forwards the attacker-chosen `shop` value straight into `WebhookMetadata` for the handler to act on [5](#0-4) .

This is exactly the "bytes verified versus bytes parsed" binding break: the bytes that are HMAC-verified (raw body) are disjoint from the bytes that determine which tenant the webhook is attributed to (`shop-domain` header).

### Impact Explanation
A tenant of a multi-tenant app (an unprivileged actor relative to other merchants) can forge webhook deliveries that the host application will attribute to a different shop. Depending on how the host app's webhook handlers use `WebhookMetadata#shop` (e.g., looking up/creating records, or processing GDPR-mandated `shop/redact`, `customers/redact`, `customers/data_request` topics that flow through this same `Registry.process` path [6](#0-5) ), this enables cross-tenant data injection, corruption, or triggering redaction/deletion logic against a victim shop's data — a cross-tenant access violation.

### Likelihood Explanation
Exploitation requires only: (1) being a legitimate app installer on at least one shop to observe one genuine webhook body+HMAC, and (2) sending an HTTP POST to the app's public webhook endpoint with a forged `shop-domain` header — no access to `api_secret_key`, access tokens, or the target shop is needed. This is reachable by any unprivileged internet user who can install the app on a store they control.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) into the signed material, or otherwise cryptographically tie the header-derived identifiers to the verified payload before trusting them — e.g., include the shop domain in `to_signable_string`, or require host apps to cross-check `request.shop` against a shop they have an active, independently-established session/webhook-registration record for, rather than trusting the header outright once HMAC-of-body passes.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and lets Shopify deliver a genuine webhook, capturing `raw_body` and header `x-shopify-hmac-sha256: <hmac>`.
2. Attacker POSTs to the app's webhook endpoint with the same `raw_body` and `x-shopify-hmac-sha256` header, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `HmacValidator.validate` succeeds because `to_signable_string` only checks `raw_body` [1](#0-0) .
4. `Registry.process` calls the registered handler with `shop: "victim-shop.myshopify.com"` [7](#0-6) , causing the host app to process attacker-controlled data under the victim's tenant identity.

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

**File:** lib/shopify_api/webhooks/registry.rb (L8-12)
```ruby
      MANDATORY_TOPICS = T.let([
        "shop/redact",
        "customers/redact",
        "customers/data_request",
      ].freeze, T::Array[String])
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
