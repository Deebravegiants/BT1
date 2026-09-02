## Title
Webhook shop-domain header is not covered by HMAC signature, enabling cross-tenant webhook forgery - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw request body only, while the `shop` (and `topic`, `webhook_id`) values that the application trusts for tenant identification are read from HTTP headers that are never included in the signed data. This breaks the binding `HMAC_valid(body) == shop_header_authenticated`, allowing any actor who can obtain one genuine `(body, hmac)` pair for the app's shared `api_secret_key` to replay it with an arbitrary `shop-domain` header and have it accepted as coming from a different (victim) shop.

### Finding Description
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery`, whose `to_signable_string` is the sole data over which the HMAC is checked: [1](#0-0) 

Meanwhile, `shop`, `topic`, and `webhook_id` are pulled straight from request headers, entirely outside the signed payload: [2](#0-1) 

`Registry.process` validates only the body's HMAC and then unconditionally trusts `request.shop` (from the unauthenticated header) to build the `WebhookMetadata` that is handed to the app's webhook handler for tenant-scoped processing (e.g. `shop/redact`, `customers/redact`, `customers/data_request`, order/product sync, etc.): [3](#0-2) 

`HmacValidator.validate` confirms only that `verifiable_query.hmac` matches `HMAC(secret, verifiable_query.to_signable_string)` — i.e. it authenticates the body, never the shop claimed alongside it: [4](#0-3) 

Because the app's `api_secret_key` is a single shared secret used to sign webhooks for *every* shop that has installed the app, a genuine, validly-signed `(body, hmac)` pair obtained for one shop (e.g., the attacker's own store, which is free to create and install the app on) remains valid when replayed with the `X-Shopify-Shop-Domain` (or `shopify-shop-domain`) header rewritten to name a different shop. The library performs no check that the signed body is bound to, or was ever associated with, the shop named in the header.

This is the direct analog of the reported bug class: a field that is *acted upon* (`shop`, used for tenant-scoped identification in `WebhookMetadata`) is not covered by the same integrity check (`hmac`) that authenticates the rest of the message, so the two can be desynchronized by an attacker who controls one but not the other.

### Impact Explanation
This breaks the equality that should hold: `authenticated_body_source_shop == shop_used_for_processing`. Any app owner-controlled shop (installable by anyone, no privileged credentials or `api_secret_key` needed) can, after capturing one legitimate outbound webhook delivery to its own endpoint, forge a webhook that the host application will attribute to an arbitrary victim shop, since the gem passes the unauthenticated `shop` header straight through to the handler after only checking the body's HMAC. Depending on how the host app uses `WebhookMetadata#shop` (e.g., to select the tenant record to update/redact/delete, as is standard for mandatory `customers/redact`, `customers/data_request`, `shop/redact` handlers), this yields cross-tenant data corruption or exfiltration — a Critical-class cross-tenant access vector per the impact criteria, achieved purely through this gem's verification logic.

### Likelihood Explanation
Moderate-to-high: exploitation requires only (1) installing the app on any shop the attacker controls (a normal, unprivileged action any internet user can take for an app with public installation), (2) capturing one legitimate webhook delivery (body + `hmac-sha256` header) sent to their own endpoint, and (3) POSTing that exact body/hmac pair to the target application's public webhook endpoint with a modified `shop-domain` header. No knowledge of `api_secret_key`, access tokens, or the victim's credentials is required.

### Recommendation
Bind the shop (and other trust-relevant metadata) into the value that is HMAC-verified, or otherwise cryptographically tie the header-derived `shop` to the request that was authenticated — e.g., include the shop domain in `to_signable_string`, or require the calling application to cross-check `request.shop` against session/registration state for that specific `webhook_id`/topic before trusting it. At minimum, document prominently that `Request#shop` is unauthenticated and must not be used as a sole tenant-selection key downstream.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` (standard app install flow, no privileged access needed).
2. Shopify delivers a legitimate webhook (e.g. `orders/create`) to the app's public endpoint with body `B` and header `X-Shopify-Hmac-Sha256: H`, where `H = HMAC-SHA256(api_secret_key, B)`. Attacker captures `B` and `H` (e.g. via a proxy on infrastructure they control, or a logging endpoint they operate).
3. Attacker crafts a new POST to the same public webhook endpoint with:
   - Body: the captured `B` (unchanged, so `H` remains valid)
   - Header `x-shopify-hmac-sha256: H` (unchanged)
   - Header `x-shopify-shop-domain: victim-shop.myshopify.com` (changed)
   - Header `x-shopify-topic`/`x-shopify-webhook-id` as desired
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `B` against `H`: [5](#0-4) 
5. The handler receives `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: parsed(B), ...)`, and the host app processes attacker-controlled data as if it originated authentically from the victim shop.

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
