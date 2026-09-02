The webhook signature-verification flow in this gem exhibits the same class of identity-binding defect described in the report: a value that downstream code trusts for tenant identification is never included in the value that the cryptographic check actually covers.### Title
Webhook `shop` (tenant) identity is trusted from an unauthenticated header while the HMAC only covers the request body - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the `shop` (tenant) identity from the `shopify-shop-domain` / `x-shopify-shop-domain` HTTP header, but the HMAC signature that `Utils::HmacValidator` verifies is computed only over the raw body. The `shop` value is therefore never bound to the cryptographic proof of authenticity that gates webhook processing, letting an unprivileged caller who possesses any one valid `(body, hmac)` pair relabel it as belonging to an arbitrary other shop.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop` is read straight from the request headers, completely outside the signed material: [2](#0-1) [3](#0-2) 

`Registry.process` validates the HMAC over that body-only string and, once it passes, forwards `request.shop` — the unauthenticated header value — straight to the app's handler as the tenant identity for the event: [4](#0-3) 

`HmacValidator.validate` confirms this: it recomputes the signature only from `verifiable_query.to_signable_string` (the body) and compares it to the received HMAC — the `shop`/`topic`/`webhook_id` headers play no role in the comparison: [5](#0-4) 

This is exactly the identity-binding gap called out by the report's bug class: "a field acted on but not covered by the HMAC." Here the field is the `shop` domain that the host application uses as its per-tenant key (session lookup, data scoping, mandatory-topic handling like `shop/redact`, `customers/redact`, `customers/data_request`): [6](#0-5) 

Because the signature never binds `shop` to `body`, any `(raw_body, hmac)` pair the gem accepts for shop A is equally valid for shop B — the check answers the question "was this body signed by our client secret?" not "did this body/shop pair come from Shopify for this specific shop?" An attacker who operates their own shop and installs the vulnerable app receives genuine webhooks (valid `body` + valid `hmac`, both computed by Shopify using the app's `client_secret`) for their own shop. They can then send an HTTP request directly to the app's public webhook endpoint with that same body/hmac but a forged `shopify-shop-domain` header naming a different (victim) shop. `Utils::HmacValidator.validate` still returns `true` because it only checks the body against the secret, and `Registry.process` hands the handler `shop: <victim shop>` alongside data the attacker fully controls (subject to the JSON structure of that webhook topic).

### Impact Explanation
This crosses the tenant boundary the gem is supposed to enforce: an unprivileged internet user (any shop owner who installs the app) can make the host application execute business logic (order/customer/GDPR handlers, inventory changes, uninstall handling, etc.) under the identity of an arbitrary victim shop, since the gem asserts the webhook is authentic and hands over an attacker-chosen `shop` value as if it were verified. This matches the "cross-tenant access" Critical-impact category: the confidentiality/integrity of one merchant's data can be affected by a request that only proves authenticity of a *body*, not of the *shop-body pairing*.

### Likelihood Explanation
Exploitation requires no special privilege beyond installing the app on a shop the attacker controls (or otherwise obtaining one legitimate webhook body+hmac, e.g. via a test/development shop) and the ability to send arbitrary HTTP requests to the app's public webhook endpoint with custom headers — both trivially available to any unprivileged internet user. No access token, `client_secret`, or credential leak is needed; the entire path is reachable through this gem's own `Webhooks::Request`/`Registry`/`HmacValidator` code as shipped.

### Recommendation
Bind the tenant identity to the signed material, or otherwise re-validate it independently of headers:
- Prefer deriving `shop` only from a source that is itself authenticated for the specific request (e.g., look up the expected shop from the webhook subscription/registration record fetched via an authenticated API call, rather than trusting the header), or
- Extend the signable payload construction so that `shop`/`topic`/`webhook_id` are cryptographically bound (e.g., re-hash `shop|topic|webhook_id|body` server-side against a value the app already possesses for that specific installation) before trusting the header for dispatch, or
- At minimum, cross-check the header `shop` against a shop the app has an active session/installation record for before invoking the handler, so a mismatched shop is rejected even when the raw body HMAC is technically valid.

### Proof of Concept
1. Attacker installs the target Shopify app on their own shop `attacker-shop.myshopify.com`.
2. Attacker triggers a webhook event (e.g. `orders/create`) and captures the resulting POST: raw body `B` and header `x-shopify-hmac-sha256: H`, both legitimately produced by Shopify using the app's `client_secret`.
3. Attacker sends a new HTTP request directly to the app's public webhook endpoint:
   - Body: `B` (unchanged)
   - Header `x-shopify-hmac-sha256: H` (unchanged)
   - Header `x-shopify-shop-domain: victim-shop.myshopify.com` (forged)
   - Header `x-shopify-topic: orders/create`
4. `ShopifyAPI::Webhooks::Request.new` parses these headers; `Utils::HmacValidator.validate` recomputes the HMAC over `B` only and it matches `H`, so validation succeeds: [7](#0-6) 
5. `Registry.process` calls the registered handler with `shop: "victim-shop.myshopify.com"` and the attacker-originated body, even though Shopify never sent this body for `victim-shop`: [8](#0-7) 
6. Any host application logic keyed on `data.shop` (session lookup, GDPR compliance actions, data mutation scoped "for this shop") now operates against the victim shop's identity using attacker-supplied content.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
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

**File:** lib/shopify_api/webhooks/request.rb (L67-70)
```ruby
      sig { params(name: String).returns(T.untyped) }
      def shopify_header(name)
        @headers["shopify-#{name}"] || @headers["x-shopify-#{name}"]
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
