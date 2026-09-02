### Title
Webhook Shop/Topic Identity Not Bound by HMAC, Enabling Cross-Tenant Webhook Spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats a webhook request as fully authenticated once `Utils::HmacValidator.validate(request)` succeeds, but the HMAC signature only covers the raw request body. The `shop`, `topic`, `api_version`, and `webhook_id` values — which are taken from unauthenticated HTTP headers and passed straight into `WebhookMetadata` for the handler to act on — are never bound to that signature.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`HmacValidator.validate` computes the HMAC exclusively over `verifiable_query.to_signable_string`: [2](#0-1) 

Meanwhile `shop`, `topic`, `api_version`, and `webhook_id` are all read from HTTP headers, not from the signed payload: [3](#0-2) 

`Registry.process` validates only the body HMAC and then unconditionally builds `WebhookMetadata` from these unauthenticated header fields, handing them to the app's handler as if they were verified: [4](#0-3) 

The library's own documentation reinforces the false assumption that the entire request is authenticated: "This will verify the request did indeed come from Shopify and then call the specified handler for that webhook." In reality only the byte content of the body is verified — the `shop` claim that host applications use to select which merchant's session/data to act on is not covered by the equality the HMAC is supposed to enforce (`hmac == HMAC(secret, signed_bytes)` where `signed_bytes` excludes `shop`).

### Impact Explanation
Any merchant can install the app on their own shop (an unprivileged, standard action) and receive a genuinely Shopify-signed webhook — the body and its HMAC are valid for that specific `raw_body`. Because the signature is independent of the `shop`/`topic`/`webhook_id` headers, that same valid `(raw_body, hmac)` pair can be replayed to the app's webhook endpoint with the `X-Shopify-Shop-Domain` header rewritten to a victim shop's domain (or the topic changed, e.g. to `shop/redact`, `customers/redact`, `customers/data_request`, or `app/uninstalled`). `Registry.process` will accept it, and the handler receives `WebhookMetadata` claiming the payload belongs to the victim shop. Downstream host-app logic that keys off `data.shop` to look up a session, write order/customer data, or trigger GDPR-mandated data deletion for "that shop" would act on the wrong tenant — a cross-tenant integrity/confidentiality break, and potentially destructive if mandatory redact topics are spoofed against a victim.

### Likelihood Explanation
Exploitation only requires the ability to install the target app on an attacker-controlled shop (a low bar for any public or unlisted app) and the ability to send an arbitrary HTTP request with attacker-chosen headers and Shopify's own signed body/HMAC to the app's public webhook endpoint. No access to `api_secret_key` or any privileged credential is required, since the attacker never needs to forge the HMAC — they replay one Shopify already computed for them.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) to the signature verification path: e.g., require the host application to check `request.shop` against a known/installed shop for the active session *before* trusting `WebhookMetadata`, and/or extend `Registry.process`/`HmacValidator` to fail closed unless the caller supplies the expected shop domain to compare against `request.shop`. At minimum, update `docs/usage/webhooks.md` to explicitly state that the HMAC only authenticates the raw body, not the shop/topic headers, and that callers must independently verify `request.shop` is the shop they expect before processing.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com` and registers a webhook (e.g., `orders/create`).
2. Shopify sends a legitimate webhook POST to the app's endpoint with body `B` and header `X-Shopify-Hmac-Sha256: HMAC(secret, B)` and `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`.
3. Attacker captures this request and re-sends it to the same endpoint, keeping body `B` and the HMAC header unchanged, but replacing `X-Shopify-Shop-Domain` with `victim-shop.myshopify.com` (and/or `X-Shopify-Topic` with `shop/redact`).
4. `Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only recomputes the HMAC over `raw_body` (`request.rb` lines 35-38) — validation succeeds.
5. The handler is invoked with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", topic: ..., body: B, ...)`, causing the host application to process attacker-supplied data under the victim shop's identity.

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
