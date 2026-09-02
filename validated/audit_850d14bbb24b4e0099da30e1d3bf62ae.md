### Title
Webhook `shop-domain` header is not bound to the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body, while `shop`, `topic`, `webhook_id`, and `api_version` are read directly from unauthenticated HTTP headers. `Utils::HmacValidator.validate` verifies the HMAC exclusively against that body, so the `shop-domain` header used to attribute the webhook to a tenant is never covered by the signature check.

### Finding Description
`Registry.process` gates webhook handling on `Utils::HmacValidator.validate(request)`: [1](#0-0) 

`HmacValidator.validate`/`validate_signature` computes the HMAC purely from `verifiable_query.to_signable_string`: [2](#0-1) 

And `Request#to_signable_string` is defined as just the raw body: [3](#0-2) 

Meanwhile `Request#shop` (and `topic`, `webhook_id`, `api_version`) are pulled straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header, which is never mixed into the signable string: [4](#0-3) 

That `shop` value is then forwarded, unauthenticated, straight to the handler as the tenant identity of the webhook: [1](#0-0) 

This breaks the identity binding: `HMAC-verified(raw_body) == HMAC-verified(raw_body)` is checked, but the equality the app actually relies on — `shop_header == shop_that_produced(raw_body, hmac)` — is never enforced. Any request whose body/HMAC pair was legitimately produced by Shopify for shop A will pass `validate` unchanged even if the attacker swaps the `x-shopify-shop-domain` header to shop B, because the header is outside the signed material.

### Impact Explanation
An app operator who is themselves a legitimate merchant installed on the app (or anyone who has observed/replayed one valid `(raw_body, hmac)` pair, e.g. from their own store's webhook deliveries) can resubmit that exact body/HMAC to the app's webhook endpoint while substituting a different shop domain in the header. `HmacValidator.validate` still returns `true`, and the handler receives `WebhookMetadata` claiming the payload belongs to the victim shop. Depending on what the host application does with `WebhookMetadata#shop` (e.g. looking up per-shop settings, writing to a per-shop record, uninstall/redact actions), this is a cross-tenant data integrity/confidentiality issue — the app is tricked into attributing attacker-controlled, HMAC-"verified" webhook data to another merchant's tenant.

### Likelihood Explanation
Exploitation requires only network access to the app's public webhook endpoint plus one previously observed valid `(body, hmac)` pair for the same `api_secret_key` — no access token, session, or `client_secret` is needed, and no privileged position is required beyond having been a normal webhook recipient at some point (or intercepting one's own legitimately delivered webhook). This is a realistic, unprivileged-internet-facing scenario, consistent with the report's underlying bug class of a security check being satisfiable through an unintended path (here: signing scope smaller than the trust decision it is used to authorize).

### Recommendation
Bind the tenant-identifying header(s) into the material that is HMAC-verified, or otherwise cross-check the header value against data derivable only from the verified body/secret. Concretely, `Request#to_signable_string` should incorporate `shop-domain` (and ideally `topic`/`webhook_id`) into the signed string, or `Registry.process`/`HmacValidator.validate` should independently re-derive/confirm the shop from the verified payload rather than trusting the header verbatim.

### Proof of Concept
1. Attacker is a merchant on shop `attacker.myshopify.com` and receives a legitimate webhook delivery with body `B` and header `x-shopify-hmac-sha256: H` (valid for the app's `api_secret_key`).
2. Attacker resends `POST /webhook` to the app with the same body `B` and same `x-shopify-hmac-sha256: H`, but sets `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {..., "x-shopify-shop-domain" => "victim.myshopify.com", "x-shopify-hmac-sha256" => H})` is constructed.
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `B` only and finds it matches `H` — validation succeeds.
5. The handler is invoked with `WebhookMetadata.new(shop: "victim.myshopify.com", body: parsed(B), ...)`, causing the app to process attacker-supplied data under the victim's tenant identity. [5](#0-4) [1](#0-0)

### Citations

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
