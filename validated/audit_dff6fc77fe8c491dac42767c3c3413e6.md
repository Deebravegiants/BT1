## Finding

### Title
Webhook `shop` and `topic` identity is not covered by the HMAC signature, enabling cross-tenant webhook forgery/replay - (`lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body, while `shop`, `topic`, `webhook_id`, and `api_version` are read directly from HTTP headers that are **not** part of the signed material. `Registry.process` accepts any request whose body/HMAC pair validates and then trusts `request.shop`/`request.topic` — taken straight from unauthenticated headers — as the tenant identity handed to the app's webhook handler.

### Finding Description
`HmacValidator.validate` computes the signature purely from `verifiable_query.to_signable_string` and the app secret: [1](#0-0) 

For webhook requests, `to_signable_string` is defined as just the raw body, while `shop`, `topic`, `webhook_id` and `api_version` come from HTTP headers that are excluded from the signable string entirely: [2](#0-1) 

`Registry.process` validates the HMAC and then unconditionally trusts `request.shop` and `request.topic` (both header-derived, unsigned) to build the metadata delivered to the app's handler: [3](#0-2) 

The binding that should hold is: **`shop` (and `topic`) used by the handler == `shop`/`topic` that the HMAC actually authenticates**. Because the HMAC only binds the body bytes, and `shop`/`topic` are separate, unauthenticated header values, this equality does not hold. An HMAC computed by Shopify for the app's `api_secret_key` is a function of *body only* — it is valid for that body regardless of which shop originally triggered the webhook containing it, and regardless of which topic header accompanies it. This is exactly the "field acted on but not covered by the HMAC" analog: the signature verifies bytes that are disjoint from the identity fields the code subsequently acts on.

### Impact Explanation
Any unprivileged actor can install the target app on their own free/trial Shopify development store (no privileged access required) and receive one legitimately-signed webhook (any topic) addressed to that store. Because the signature covers only the raw body — not `shop-domain` or `topic` — the attacker can replay that exact `(body, hmac)` pair to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header with an arbitrary victim shop domain and/or the `X-Shopify-Topic` header with a different topic (e.g. `customers/redact`, `shop/redact`, `app/uninstalled`). `Registry.process` will accept it as authentic and invoke the app's handler with `WebhookMetadata.shop` set to the attacker-chosen victim domain, causing shop-scoped business logic (data deletion workflows, app-uninstall cleanup, entitlement changes, audit logging, etc.) to execute under an identity the attacker never authenticated for. This is a cross-tenant identity-binding break satisfying the Critical impact bar.

### Likelihood Explanation
Requires only: (1) ability to install the app on any store the attacker controls (unprivileged, self-service), and (2) capturing one webhook HTTP request via a normal request interception (any HTTP proxy) — no access token, `client_secret`, or privileged credentials are needed. The forged replay is a standard HTTP request with two header values changed. This is a low-effort, unprivileged attack path fully contained within this gem's webhook validation logic.

### Recommendation
Bind the identity fields into the signed material, or otherwise cryptographically tie `shop`/`topic` to the signature:
- Extend `to_signable_string` (or add a separate integrity check) to include `shop-domain`, `topic`, and `webhook-id` alongside the body, so any header tampering invalidates the HMAC, or
- Have `Registry.process` cross-check the header-derived `shop`/`topic` against values embedded in the parsed body payload (Shopify webhook payloads generally carry shop/topic-consistent data) before dispatching to handlers, and reject mismatches.
- At minimum, document and enforce that consumers of `WebhookMetadata#shop`/`#topic` must not treat these as authenticated unless additionally corroborated, and provide a library-level safeguard rather than relying on downstream app code to notice.

### Proof of Concept
1. Attacker creates a free Shopify partner/dev store `attacker-shop.myshopify.com` and installs the target app; the app registers a webhook (e.g. `orders/create`).
2. Shopify delivers a legitimate webhook to the app with raw body `B` and header `X-Shopify-Hmac-Sha256: H` (`H = HMAC-SHA256(api_secret_key, B)`), `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`, `X-Shopify-Topic: orders/create`. Attacker records `B` and `H` via a local proxy.
3. Attacker sends a forged POST to the app's public webhook endpoint reusing body `B` and header `H`, but sets:
   - `X-Shopify-Shop-Domain: victim-shop.myshopify.com`
   - `X-Shopify-Topic: customers/redact` (or any registered topic)
4. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: forged_headers)` is constructed; `HmacValidator.validate(request)` recomputes `HMAC-SHA256(api_secret_key, B)` and it matches `H` (per `lib/shopify_api/utils/hmac_validator.rb`), because the signature never depended on the headers.
5. `Registry.process` proceeds and calls the registered `customers/redact` handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", topic: "customers/redact", ...)` (`lib/shopify_api/webhooks/registry.rb:198-199`), causing the app to execute victim-shop-scoped logic that the attacker neither owns nor was authorized by Shopify to trigger for that shop.

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
