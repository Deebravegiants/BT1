### Title
Webhook shop-domain header is not covered by the HMAC signature, breaking the `hmac ↔ shop` identity binding - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#hmac` is validated only against the raw request body, while `ShopifyAPI::Webhooks::Request#shop` is read from an unauthenticated HTTP header (`x-shopify-shop-domain`/`shopify-shop-domain`). `ShopifyAPI::Webhooks::Registry.process` treats a valid body HMAC as proof that the entire request — including the shop identity — is authentic, and forwards the header-derived `shop` value straight to the host application's webhook handler. The binding "HMAC covers signed bytes == bytes the app trusts as the tenant identity" does not hold, because the shop identifier is bytes that are parsed but never verified.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, `topic`, `webhook_id`, and `api_version` are all pulled from headers that are completely outside the signed material: [2](#0-1) 

`ShopifyAPI::Webhooks::Registry.process` validates the HMAC and, on success, unconditionally uses `request.shop` (the unauthenticated header) to build the `WebhookMetadata` passed to the app's handler: [3](#0-2) 

`ShopifyAPI::Utils::HmacValidator.validate` only compares `verifiable_query.hmac` against a signature computed from `to_signable_string`, so it certifies the body, not the shop: [4](#0-3) 

Because Shopify's webhook payload for most topics does not embed the shop domain inside the JSON body (the shop is only conveyed via the header), the only integrity guarantee provided by this gem is "this exact body was signed with the app secret at some point." It is not "this body was sent for this shop." Any request whose body/HMAC pair is a legitimately-obtained Shopify webhook (e.g. one the attacker's own store received, since any unprivileged user can install a public app on their own store and receive real signed webhooks) can be replayed with the `x-shopify-shop-domain` header swapped to a victim shop domain. `Registry.process` will accept it as valid and hand the victim's shop identifier plus the attacker's body to the handler.

This mirrors the report's bug class: a value used to make a tenant-scoped decision (`shop`) is disjoint from the bytes actually verified by the cryptographic check (`raw_body`), i.e. "bytes verified versus bytes parsed."

### Impact Explanation
Handlers built on top of this gem (per the documented usage pattern in `docs/usage/webhooks.md`) key all downstream behavior — e.g. enqueuing background jobs, updating per-shop records, triggering GDPR/compliance webhooks, uninstall cleanup, billing changes — off `WebhookMetadata#shop`. Because that field is not bound to the signature, an attacker can make an application believe a webhook payload (fully attacker-controlled JSON body, since it need not correspond to real victim data) originated from a shop they do not own, causing the host app to process attacker data or attacker-triggered events under a victim tenant's identity. This is a cross-tenant identity confusion, matching the Critical "cross-tenant access" impact category.

### Likelihood Explanation
High: the only prerequisite is the ability to install any Shopify app that uses this webhook flow on an account the attacker controls (unprivileged, ordinary merchant action) in order to obtain a body/HMAC pair signed with the app's secret, and then resending that request to the app's public webhook endpoint with a modified `shop-domain` header. No access to `api_secret_key`, tokens, or TLS interception is required — the header is simply never checked against the signature.

### Recommendation
Include the shop domain (and ideally topic/webhook id) in the signed material verified against the HMAC, or otherwise cryptographically/contextually bind the header-derived `shop` to the verified request (e.g., require the caller to additionally confirm the shop against an installed-shop store before trusting `WebhookMetadata#shop`). At minimum, document loudly and enforce in `Registry.process` that `request.shop` must be cross-checked against a known/installed shop list before being handed to `handler.handle`.

### Proof of Concept
1. Attacker installs the target public app on their own store `attacker.myshopify.com` and registers/receives a legitimate webhook (any topic) — Shopify sends body `B` with header `x-shopify-hmac-sha256: HMAC(secret, B)` and `x-shopify-shop-domain: attacker.myshopify.com`.
2. Attacker resends the exact same body `B` and HMAC header to the app's webhook endpoint, but replaces `x-shopify-shop-domain` with `victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: modified_headers)` succeeds (all required headers present).
4. `ShopifyAPI::Webhooks::Registry.process(request)` calls `Utils::HmacValidator.validate(request)`, which passes because it only recomputes HMAC over `B` — see: [5](#0-4) 
5. The handler receives `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: JSON.parse(B), ...)` and performs its tenant-scoped side effects against the victim shop, even though the victim never sent this webhook.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
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
```
