This confirms the finding. The webhook `Request` object's `to_signable_string` returns only `@raw_body` [1](#0-0) , meaning the Shopify-computed HMAC exclusively signs the request body, while `shop`, `topic`, `webhook_id`, and `api_version` are all read directly from HTTP headers that are entirely outside the signature's coverage [2](#0-1) . `Registry.process` validates only the HMAC and then dispatches the handler using the unauthenticated `request.shop` and `request.topic` values [3](#0-2) .

### Title
Webhook tenant/topic attribution (`shop`, `topic`) not covered by HMAC allows cross-tenant webhook forgery - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` derives the `shop` (and `topic`, `webhook_id`, `api_version`) values from HTTP headers, but the HMAC signature verified by `HmacValidator` is computed over the raw body only. This breaks the intended binding `hmac == HMAC(secret, body || shop || topic)`; in reality `hmac == HMAC(secret, body)`, with `shop`/`topic` unauthenticated.

### Finding Description
`Utils::HmacValidator.validate` computes `compute_signature(verifiable_query.to_signable_string, secret)` and compares it to the received HMAC [4](#0-3) . For webhook requests, `to_signable_string` is simply `@raw_body` [1](#0-0) . The `shop`, `topic`, `webhook_id`, and `api_version` accessors read straight from headers with no cryptographic binding to the signature [2](#0-1) .

`Registry.process` trusts these unauthenticated fields once the body HMAC checks out: it raises only if the HMAC is invalid, then builds `WebhookMetadata` directly from `request.topic`, `request.shop`, and `request.webhook_id` and invokes the registered handler with them [3](#0-2) .

The app's `api_secret_key` used to compute the HMAC is shared across every shop that installs the app — it is not per-shop. Because of this, the identity binding that matters (which shop a webhook body belongs to) is exactly the piece excluded from the signed bytes.

### Impact Explanation
This is a cross-tenant boundary violation: any party who can obtain one genuine `(body, hmac)` pair signed with the app's shared secret — e.g., a merchant who installed the app and can observe/replay webhooks delivered to their own endpoint — can resend that exact body/HMAC pair to the app's webhook endpoint with an arbitrary `x-shopify-shop-domain` (and `x-shopify-topic`) header. `Utils::HmacValidator.validate` will report it valid because it only checks the body bytes, and `Registry.process` will hand the forged `shop`/`topic` straight to the host application's webhook handler as if Shopify itself vouched for that attribution. This lets an attacker inject data attributed to a victim shop (or reinterpret a body under a different topic than the one Shopify signed it for), i.e., cross-tenant data injection through the gem's own webhook dispatch logic.

### Likelihood Explanation
Exploitability requires only: (1) installing the app on any shop to receive a legitimately signed webhook body/HMAC, and (2) sending an HTTP request to the app's webhook endpoint with that body/HMAC and forged shop/topic headers. No access token, `api_secret_key`, or privileged account is required — this is achievable by any unprivileged actor who can install the target app on a store they control, which is a standard, low-barrier action.

### Recommendation
Include `shop`, `topic`, and `webhook_id` in the signable content actually verified against the HMAC (Shopify's own webhook HMAC is computed over the body, so instead the gem should independently bind those header values to the verified shop/topic context, e.g., by requiring the caller to supply/verify the expected shop out-of-band, or by rejecting/re-deriving `shop`/`topic` from a source that is cryptographically tied to the request, not from unauthenticated headers alone). At minimum, document prominently that `request.shop`/`request.topic` are not covered by the HMAC and must not be trusted for tenant attribution without additional verification (e.g., cross-checking against a known/expected shop per registration).

### Proof of Concept
1. App is installed on `attacker.myshopify.com`; Shopify delivers a webhook: body `{"id":123}`, headers include `x-shopify-hmac-sha256: <valid hmac of body>`, `x-shopify-shop-domain: attacker.myshopify.com`, `x-shopify-topic: orders/create`.
2. Attacker captures `raw_body` and `hmac` from this genuine delivery (they control the endpoint that receives it, or intercept it via their own logging).
3. Attacker sends a new POST to the app's webhook endpoint with the identical `raw_body` and `x-shopify-hmac-sha256`, but sets `x-shopify-shop-domain: victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` parses headers; `Utils::HmacValidator.validate` recomputes HMAC over `raw_body` only and it matches, so `Registry.process` proceeds [5](#0-4) .
5. The registered handler receives `WebhookMetadata` with `shop: "victim.myshopify.com"` and processes attacker-supplied data as if it originated from the victim's store [6](#0-5) .

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
