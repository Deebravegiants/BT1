### Title
Webhook `shop` (and `topic`/`api_version`/`webhook_id`) identity fields are not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (`lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by verifying an HMAC over the raw request **body**. The `shop` (and `topic`/`api_version`/`webhook_id`) values used to identify the tenant and dispatch the webhook to the app's handler are read straight from unauthenticated HTTP headers that are never included in the signed content. Any request whose body/HMAC pair is valid for the shared secret can be replayed with an arbitrary `shop` header, so the authenticated "this body was HMAC-signed by Shopify" guarantee is bound to the wrong identity field.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

and `shop`, `topic`, `api_version`, `webhook_id` are all pulled directly from the (attacker-suppliable) HTTP headers, independent of the signature: [2](#0-1) [3](#0-2) 

`Utils::HmacValidator.validate` computes/compares the signature exclusively against `to_signable_string` (the body), never the headers: [4](#0-3) 

`Registry.process` trusts this unauthenticated `shop` value and forwards it straight into the handler's `WebhookMetadata`, which is the value host applications typically use as the tenant/session key to decide whose data to update: [5](#0-4) 

The identity binding that should hold is: `shop the HMAC authenticates == shop the app acts on`. Because the HMAC only covers the body, this equality is never enforced — an attacker who legitimately receives (or triggers) a webhook for their own installed shop (a valid `body` + `hmac` pair, since they are a real merchant with the app installed) can resend the exact same body/HMAC to the app's webhook endpoint while substituting the `x-shopify-shop-domain` (and/or `x-shopify-topic`) header for a victim shop. `HmacValidator.validate` still returns `true` (it never looked at the header), and `Registry.process` dispatches the handler with `shop: <victim>` while the body content is fully attacker-controlled.

### Impact Explanation
This breaks the tenant isolation identity binding ("shop authenticated" vs. "shop acted upon") explicitly called out as an in-scope analog. A host application that uses `WebhookMetadata#shop` as the session/tenant key (the documented and expected usage pattern for this gem's webhook handler interface) will process attacker-controlled webhook bodies under a victim shop's identity — e.g., creating/updating/deleting records keyed by the victim's shop, or triggering shop-scoped business logic (uninstall handling, order/customer processing, etc.) for a shop the attacker does not own. This is a cross-tenant access issue reachable by any unprivileged internet user who can install the app on their own store (a normal, unprivileged action) — no access token, `client_secret`, or leaked credential is required.

### Likelihood Explanation
High. The attacker only needs a legitimately signed webhook for their own shop (trivially obtainable by installing the target app on a shop they control and triggering any webhook topic), and the ability to POST arbitrary HTTP requests with custom headers to the app's public webhook endpoint. No secret material or privileged access is required.

### Recommendation
Bind the tenant-identifying fields to the signed content instead of trusting unauthenticated headers:
- Include `shop`, `topic`, and other identity-relevant headers in the HMAC-signed payload (`to_signable_string`) so tampering invalidates the signature, or
- Cross-check the `shop`/`topic` headers against the value embedded in the (already-authenticated) webhook body payload where Shopify includes it, and reject on mismatch, and
- Document clearly for consumers that `WebhookMetadata#shop`/`topic` must not be trusted as tenant keys unless independently re-validated (e.g., confirmed against a locally-stored access token for that shop before acting).

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker-shop.myshopify.com` and triggers a webhook (e.g. `orders/create`), capturing the request body `B` and its valid `x-shopify-hmac-sha256` header `H` (computed by Shopify over `B` with the app's shared secret).
2. Attacker POSTs to the app's public webhook endpoint with the same body `B` and header `H`, but sets:
   - `x-shopify-shop-domain: victim-shop.myshopify.com`
   - (optionally) a different `x-shopify-topic`
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only recomputes HMAC over `B` and matches `H` → validation succeeds.
4. The registered handler is invoked with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: <attacker-controlled parsed body>, ...)`, causing the host app to act on victim-shop's tenant data using attacker-supplied content.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

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

**File:** lib/shopify_api/webhooks/request.rb (L66-70)
```ruby

      sig { params(name: String).returns(T.untyped) }
      def shopify_header(name)
        @headers["shopify-#{name}"] || @headers["x-shopify-#{name}"]
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
