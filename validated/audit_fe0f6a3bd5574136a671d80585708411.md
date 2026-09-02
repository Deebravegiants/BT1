This confirms the vulnerability path. The `Bridge`-style "checks not applied on the retry/alternate path" bug class maps directly to `ShopifyAPI::Webhooks::Request` and `ShopifyAPI::Utils::HmacValidator`: the HMAC only binds `@raw_body` [1](#0-0) , while `shop` (and `topic`/`webhook_id`) are read directly from unauthenticated headers [2](#0-1) . `HmacValidator.validate` only ever checks `verifiable_query.to_signable_string` against the secret [3](#0-2) , so the `shop` header carries no cryptographic binding to the signed body. `Registry.process` then trusts `request.shop` verbatim to build the `WebhookMetadata` dispatched to the host app's handler [4](#0-3) .

Since `api_secret_key` (the app's single client_secret) is shared across every merchant that installs the app, any merchant who receives a legitimately-signed webhook for their own store can replay that exact body+HMAC pair while swapping the `shop-domain` header, causing the gem to hand the host app a `WebhookMetadata` claiming the event came from a different, victim shop — a cross-tenant identity-binding break, entirely reachable by an unprivileged (but app-installing) internet user, with no need for `api_secret_key`, an access token, or privileged access.

### Title
Webhook HMAC does not bind the `shop-domain` header, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body [1](#0-0) , while `shop`, `topic`, and `webhook_id` are taken straight from HTTP headers that are never included in the HMAC computation [5](#0-4) . `Utils::HmacValidator.validate` computes and compares the signature solely over `verifiable_query.to_signable_string` [3](#0-2) . Consequently a valid HMAC only proves the *body* is authentic; it proves nothing about which shop the event is attributed to.

### Finding Description
`Registry.process` validates the HMAC and then immediately builds `WebhookMetadata` using `request.shop`, `request.topic`, and `request.webhook_id` — all header-derived and unauthenticated by the signature — and forwards it to the host app's handler [4](#0-3) .

Because `api_secret_key` is the app's single shared secret across all installing merchants (not per-tenant), any merchant who installs the app can:
1. Trigger a real Shopify webhook to their own callback endpoint (a legitimate action for their own store), capturing a genuine `body` + HMAC.
2. Resend that same `raw_body`/`hmac-sha256` pair to the app's webhook endpoint, but with an arbitrary `shop-domain` header (e.g., a victim merchant's domain).
3. `HmacValidator.validate` succeeds because it only re-computes the HMAC over `raw_body`, which is unchanged. `Registry.process` then dispatches to the handler with `shop` = attacker-chosen victim domain [4](#0-3) .

This breaks the intended identity binding: "shop the webhook event is attributed to" == "shop that Shopify actually generated the event for." Any host app that uses `data.shop` to select the tenant record (as recommended in the gem's own documentation and example handler) can be made to apply attacker-controlled webhook data to another tenant's record — a cross-tenant integrity/access violation.

### Impact Explanation
Critical — cross-tenant access. A malicious but otherwise unprivileged app-installing merchant can forge the `shop` attribution of a webhook event that is dispatched by this gem to the host application, causing state changes (e.g., spoofed `app/uninstalled`, `shop/update`, `orders/create`, etc.) to be applied against a different, victim tenant's records in the host application, without ever possessing the app's `client_secret` or any victim credentials.

### Likelihood Explanation
High. The only prerequisite is installing the target app on any store (a normal, unprivileged action) to obtain one genuine signed webhook body, then replaying it with a different `shop-domain` header value against the app's public webhook endpoint. No secrets, tokens, or victim interaction are required.

### Recommendation
Include `shop-domain` (and ideally `topic`/`webhook_id`/`api-version`) in the value that `Utils::HmacValidator` verifies for `ShopifyAPI::Webhooks::Request`, or otherwise cryptographically bind the header-derived `shop` to the signed body (e.g., recompute/validate using a canonical string that concatenates the headers with the body) before constructing `WebhookMetadata` in `Registry.process`.

### Proof of Concept
1. Install the target app on attacker-controlled store `attacker.myshopify.com`; trigger a subscribed webhook topic (e.g., `orders/create`) so Shopify POSTs a legitimately-signed request to the app's webhook endpoint. Capture the raw body `B` and the `X-Shopify-Hmac-Sha256` header value `H` (valid because `H = HMAC-SHA256(api_secret_key, B)`, per `HmacValidator.compute_signature` [6](#0-5) ).
2. Replay a new HTTP request to the same webhook endpoint with identical body `B` and header `X-Shopify-Hmac-Sha256: H`, but set `X-Shopify-Shop-Domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `B` against `H` [4](#0-3) .
4. The handler receives `WebhookMetadata` with `shop: "victim.myshopify.com"` and body `B`, even though the event actually originated from `attacker.myshopify.com`.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L33-40)
```ruby
        sig { params(signable_string: String, secret: String).returns(String) }
        def compute_signature(signable_string, secret)
          OpenSSL::HMAC.hexdigest(
            OpenSSL::Digest.new("sha256"),
            secret,
            signable_string,
          )
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
