### Title
Webhook `shop` and `topic` identity are not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request **body**. The `shop`, `topic`, `webhook_id`, and `api_version` values — which are taken from HTTP headers and handed to the application's webhook handler as the trusted identity of the event — are never included in the signed content. This breaks the intended binding `hmac-authenticated bytes == webhook identity metadata acted upon`.

### Finding Description
`Request#to_signable_string` only returns the raw body: [1](#0-0) 

`Utils::HmacValidator.validate` computes the HMAC exclusively over `verifiable_query.to_signable_string`, i.e. only the body: [2](#0-1) 

`Registry.process` uses this same HMAC check as the sole authentication gate, then trusts `request.shop`, `request.topic`, and `request.webhook_id` — none of which were part of the signed payload — to build the metadata that is dispatched to the application's handler: [3](#0-2) 

The `shop`, `topic`, and `webhook_id` fields are read directly from attacker-controllable HTTP headers: [4](#0-3) 

Because none of these header values are part of the signed content, the equality the library implicitly claims to guarantee — `shop authenticated by HMAC == shop delivered to handler` — does not hold. An attacker who possesses **any** one genuine `(body, hmac)` pair (e.g., a webhook legitimately delivered to their own, unprivileged shop) can replay that exact body/HMAC to the app's webhook endpoint while substituting `x-shopify-shop-domain` (and/or `x-shopify-topic`) with a victim shop's domain. `HmacValidator.validate` will report success, since it only re-computes the HMAC over the untouched body, and the forged `shop`/`topic` metadata is passed straight to the application's handler as if it genuinely originated from that identity.

### Impact Explanation
This is a cross-tenant identity-binding break: an unprivileged attacker (any merchant who has installed the app and can capture one legitimate webhook delivery to their own store) can cause the library to report an event as belonging to an arbitrary other shop and/or arbitrary topic supported by the app, without ever needing the app's `client_secret` or any credential belonging to the victim. Depending on how the host app's registered handlers act on `WebhookMetadata#shop`/`#topic` (e.g. GDPR `shop/redact`, `customers/data_request`, `app/uninstalled`, order/customer webhooks used to key per-tenant storage), this can lead to cross-tenant data corruption, incorrect de-provisioning, or data leakage — matching the "cross-tenant access" Critical impact category.

### Likelihood Explanation
Exploitation only requires the attacker to be a legitimate (even free/unprivileged) merchant able to trigger one webhook delivery to themselves and directly POST to the app's public webhook endpoint with modified headers and the captured body/HMAC. No access to `api_secret_key`, access tokens, or the app's infrastructure is required, making this practically reachable by any external, unprivileged party.

### Recommendation
Bind the authenticated content to the identity fields the application acts on. At minimum, `Request#to_signable_string` (or `HmacValidator`) should incorporate `shop`, `topic`, and `webhook_id` header values into the signed material, or `Registry.process` should independently cross-check that the shop/topic implied by the body (if derivable) match the header values before dispatching to handlers. Documentation for `Registry.process` / `WebhookMetadata` should also make explicit that `shop`/`topic` are not currently authenticated by the HMAC, so consuming apps don't rely on them for tenant-scoping decisions without additional verification.

### Proof of Concept
1. Attacker installs the app on their own store `attacker-shop.myshopify.com` and receives a legitimate webhook delivery with body `B` and header `x-shopify-hmac-sha256: H` (valid HMAC of `B` under the app's secret).
2. Attacker sends a raw HTTP POST directly to the app's webhook endpoint with:
   - body: `B` (unchanged)
   - `x-shopify-hmac-sha256: H` (unchanged, still valid since body unchanged)
   - `x-shopify-shop-domain: victim-shop.myshopify.com` (forged)
   - `x-shopify-topic: shop/redact` or any topic the attacker prefers (forged)
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which returns `true` because only `B` is verified.
4. The registered handler receives `WebhookMetadata.new(topic: "shop/redact", shop: "victim-shop.myshopify.com", body: parsed(B), ...)`, believing the event genuinely originated from `victim-shop.myshopify.com`.

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
