### Title
Webhook `shop` identity is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` only signs the raw request body, while the `shop` (and `topic`) values used to dispatch and process the webhook are read directly from unauthenticated HTTP headers. This breaks the identity binding `HMAC-verified-bytes == bytes-acted-on`: the signature only proves the body came from a request signed with the app's `api_secret_key`, but says nothing about which shop that request is "for." Any tenant of a multi-tenant app can therefore present a validly-HMAC'd webhook body under a different shop's identity.

### Finding Description
`Utils::HmacValidator.validate` verifies the request by recomputing an HMAC over `verifiable_query.to_signable_string` and comparing it to the `hmac` field with `OpenSSL.secure_compare`: [1](#0-0) 

For webhooks, `Webhooks::Request` implements `to_signable_string` as simply the raw JSON body, and separately exposes `shop`, `topic`, etc. straight from HTTP headers with no cryptographic binding to that body: [2](#0-1) 

`Registry.process` validates the HMAC of the body, then immediately trusts `request.shop` (an unauthenticated header) to build the `WebhookMetadata` handed to the app's handler: [3](#0-2) 

Because every shop that installs a given app shares the same `api_secret_key`, a legitimate but malicious merchant (an unprivileged actor relative to any other tenant) can capture a genuine webhook Shopify sent for their own store — valid body + valid `x-shopify-hmac-sha256` — and replay it to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header for a victim shop. The signature check still passes because the header is not part of `to_signable_string`; `Registry.process` then invokes the handler with `shop: <victim shop>` sourced from that same untrusted header, while the actually verified bytes (the body) never asserted whose shop this was.

This is exactly the identity-binding gap the report class describes: a value ("token"/claim index in the original report; here, `shop`) is *acted on* by downstream logic but is not itself covered by the authenticity check (HMAC), only a co-located value is. Equality that should hold — `shop-header == shop-bound-by-signature` — is never actually enforced; the code accepts `shop-header ∈ {any value}` as long as the unrelated body+secret pair validates.

### Impact Explanation
If the host application's webhook handler uses `WebhookMetadata#shop` to select which tenant's stored access token/session or data to act on (a common and API-documented pattern for this gem, e.g. loading a session by shop to make subsequent authenticated calls, or writing incoming data keyed by shop), an attacker-controlled `shop` value lets one tenant inject processed events, tokens' side effects, or data attribution into another tenant's context — a cross-tenant boundary violation attributable to this gem's own webhook verification API. This maps to the specified Critical impact of cross-tenant access.

### Likelihood Explanation
Exploitation only requires the attacker to be a real, installed merchant of the target app (no leaked credentials, no TLS interception, no social engineering of the victim) — they legitimately receive a signed webhook from Shopify for their own shop and merely replay it to the shared endpoint with a modified `shop-domain` header. This satisfies the "unprivileged internet user" bar relative to any other tenant of the app.

### Recommendation
Bind the shop identity into the signed material, or otherwise cryptographically verify it, before trusting `request.shop`/`WebhookMetadata#shop`. At minimum, `Webhooks::Request#to_signable_string` should not be the only authenticity signal used to accept `shop`; document/require that consuming applications independently authenticate the shop (e.g., cross-check against a known installed-shop record) before using the header value, or extend the signable string / verification step to assert the header matches an expected value tied to the webhook's registration/session rather than trusting it implicitly.

### Proof of Concept
1. Merchant A installs the app; Shopify sends a legitimate webhook to the app's endpoint with headers `x-shopify-shop-domain: shop-a.myshopify.com`, `x-shopify-hmac-sha256: <valid hmac over body B>`, and body `B`.
2. Merchant A (attacker) intercepts/replays this exact request but changes the header to `x-shopify-shop-domain: shop-victim.myshopify.com`, keeping body `B` and the same HMAC.
3. `Utils::HmacValidator.validate` recomputes the HMAC over `B` only [4](#0-3)  — it matches, since `B` and the shared secret are unchanged.
4. `Registry.process` calls the registered handler with `shop: request.shop` == `shop-victim.myshopify.com` [5](#0-4) , causing the app to process attacker-supplied data/body under the victim shop's identity.

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
