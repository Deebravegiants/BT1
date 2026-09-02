## Title
Webhook Shop-Domain (and Topic) Header Not Covered by HMAC Signature Enables Cross-Tenant Webhook Spoofing - (`lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating an HMAC computed over the raw request body. The `shop` (and `topic`) values that the gem hands to the app's handler — and that the host application uses to attribute the webhook payload to a specific merchant/tenant — are read from HTTP headers that are never included in the signed data. Anyone holding one valid `(raw_body, hmac)` pair for the shared app `client_secret` can therefore replay it with an arbitrary `shop-domain` header and have the gem authenticate the request as coming from a different shop.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

while `shop`, `topic`, `api_version`, and `webhook_id` are pulled straight from HTTP headers with no cryptographic binding to the body: [2](#0-1) 

`Registry.process` validates the request using only this HMAC-over-body check, then immediately trusts `request.shop`/`request.topic` from the unsigned headers to build the `WebhookMetadata` passed to the app's handler: [3](#0-2) 

`Utils::HmacValidator.validate` confirms this — it only checks `verifiable_query.hmac` against `compute_signature(verifiable_query.to_signable_string, secret)`, i.e., against the body only: [4](#0-3) 

The identity-binding equality the rules describe is broken here: `authenticated(hmac) == body_bytes`, but `acted_on(shop-domain header) != authenticated(hmac)`. Because the app's `client_secret` (used to compute/verify the HMAC) is shared across every merchant that installs the app, a webhook body+HMAC pair that is genuinely valid for shop A's webhook is equally "valid" when replayed with the `shopify-shop-domain` header rewritten to shop B — the signature check does not encode which shop it belongs to.

### Impact Explanation
This is a cross-tenant identity confusion in a multi-tenant app: a merchant who legitimately receives real webhooks for their own shop (or anyone who can capture one, e.g. via their own store's webhook logs or an intermediary they control) can resubmit the same signed body to the app's webhook endpoint while claiming a different `shop-domain`. Since `Registry.process` trusts this header once the body-only HMAC checks out, the host application's handler will process/store that payload as if it came from an arbitrary victim shop of the same app, corrupting or spoofing that tenant's data (e.g. faking `orders/create`, `shop/redact`, or `customers/redact` events attributed to a shop the attacker does not control). This crosses a tenant boundary using only unprivileged access to the attacker's own installed shop, matching the "cross-tenant access" impact category.

### Likelihood Explanation
Exploitation only requires: (1) the attacker's own shop having installed the app (an unprivileged, ordinary merchant action) and being able to capture one legitimate webhook body+HMAC issued to them, and (2) sending a forged HTTP request directly to the app's public webhook endpoint with the same body/HMAC but a different `X-Shopify-Shop-Domain` header. No access to `api_secret_key`, access tokens, or the target shop's credentials is required, since the signature never covers the shop identity.

### Recommendation
Include the shop domain (and ideally topic/api_version/webhook_id) in the signed/verified material, or otherwise cryptographically bind the header values to the payload before trusting them — e.g., require the host app to cross-check `request.shop` against a known, previously-registered shop/session before dispatching to a handler, and document this requirement prominently. At minimum, the gem's documentation and `WebhookMetadata` contract should make explicit that `shop` is unauthenticated header data and must be independently validated by the consuming application against its own session store.

### Proof of Concept
1. App A has two merchants installed: `shop-a.myshopify.com` (attacker-controlled) and `shop-b.myshopify.com` (victim).
2. Shopify sends a legitimate webhook to the app for `shop-a`:
   ```
   POST /webhooks
   x-shopify-topic: orders/create
   x-shopify-hmac-sha256: <valid HMAC of raw_body computed with app client_secret>
   x-shopify-shop-domain: shop-a.myshopify.com
   <raw_body JSON>
   ```
3. Attacker (who owns `shop-a` and can observe/capture this request, e.g. from their own server logs since it was destined for them) resends the identical `raw_body` and `x-shopify-hmac-sha256` value to the app's webhook endpoint, but sets:
   ```
   x-shopify-shop-domain: shop-b.myshopify.com
   ```
4. `ShopifyAPI::Utils::HmacValidator.validate(request)` recomputes the HMAC over `@raw_body` only [5](#0-4)  and it matches, since the body and secret are unchanged.
5. `Registry.process` proceeds and calls `handler.handle(data: WebhookMetadata.new(..., shop: "shop-b.myshopify.com", ...))` [6](#0-5) , causing the host app to process attacker-supplied data as if it originated from `shop-b`.

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

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery).returns(T::Boolean) }
        def validate(verifiable_query)
          return false unless verifiable_query.hmac

          result = validate_signature(verifiable_query, Context.api_secret_key)
          if result || Context.old_api_secret_key.nil? || T.must(Context.old_api_secret_key).empty?
            result
          else
            validate_signature(verifiable_query, T.must(Context.old_api_secret_key))
          end
        end

        private

        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
